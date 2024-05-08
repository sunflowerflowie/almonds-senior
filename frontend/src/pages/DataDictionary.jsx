import { useState, useEffect } from "react";
import { useParams, useLocation } from "react-router-dom";
import api from "../api";
import Navbar from "../components/Navbar";
import "../styles/DataDictionary.css";
import jsPDF from "jspdf";

function DataDictionary() {
  const { connection_id } = useParams();
  const [dataDictionary, setDataDictionary] = useState([]);
  const [saving, setSaving] = useState(false);
  const location = useLocation();
  const connectionDetails = location.state?.form;

  useEffect(() => {
    console.log("Connection Details:", connectionDetails);

    const fetchDataDictionary = async () => {
      const tablesResponse = await api.get(`/catalog/tables/${connection_id}`);

      const promises = tablesResponse.data.tables.map((table) =>
        api
          .get(`/catalog/attributes/${connection_id}/${table.table_name}`)
          .then((response) => ({
            tableName: table.table_name,
            attributes: response.data.attributes.map((attr) => ({
              ...attr,
              description: attr.description,
              attribute_id: attr.attribute_id,
            })),
            error: !response.data.attributes,
          }))
      );
      const results = await Promise.all(promises);
      console.log(results);

      setDataDictionary(results);
    };

    fetchDataDictionary();
  }, [connection_id]);

  // Function to generate and download PDF
  const generatePDF = () => {
    const doc = new jsPDF("p", "pt", "a4");
    doc.html(document.querySelector(".data-dictionary"), {
      callback: function (pdf) {
        pdf.save("data-catalog.pdf");
      },
      x: 10,
      y: 10,
      width: 595.28,
      windowWidth: document.documentElement.offsetWidth,
    });
  };

  // Function to handle Description change
  const handleDescriptionChange = (e, attr) => {
    setDataDictionary((prevData) =>
      prevData.map((table) => ({
        ...table,
        attributes: table.attributes.map((a) =>
          a === attr ? { ...a, description: e.target.value } : a
        ),
      }))
    );
  };

  // Function to handle data format change
  const handleSaveChanges = async () => {
    setSaving(true);
    try {
      await Promise.all(
        dataDictionary.flatMap((table, index) =>
          table.attributes.map((attr) => {
            const { attribute_id, column_name, description } = attr;

            if (description != "") {
              return api.patch(`/catalog/update/${attribute_id}/`, {
                description: description,
              });
            } else {
              return;
            }
          })
        )
      );
    } catch (error) {
      console.error("Error saving changes:", error);
    } finally {
      setSaving(false);
    }
  };

  const auto_height = (elem) => {
    elem.style.height = "1px";
    elem.style.height = `${elem.scrollHeight}px`;
  };

  return (
    <div className="data-dictionary">
      <Navbar />
      <div className="content-container">
        <h1>Metadata</h1>
        <table className="detail">
          <tbody>
            <tr>
              <td>
                <b>Database Name:</b> dvdrental
                {connectionDetails?.database_name}
              </td>
            </tr>
            <tr>
              <td>
                <b>Description:</b> Sales{connectionDetails?.description}
              </td>
            </tr>
            <tr>
              <td>
                <b>Data owner:</b> CEO{connectionDetails?.department_name}
              </td>
            </tr>
          </tbody>
        </table>
        <div className="data-dictionary-button-container">
          <button
            onClick={handleSaveChanges}
            disabled={saving}
            className="save-button"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <button onClick={generatePDF} className="data-dictionary-button">
            Export as PDF
          </button>
        </div>
        {dataDictionary.map((table, index) => (
          <div key={index} className="table-container">
            <h1>{table.tableName}</h1>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Column Name</th>
                  <th>Description</th>
                  <th>Type</th>
                  <th>Primary Key</th>
                  <th>Foreign Key</th>
                </tr>
              </thead>
              <tbody>
                {table.attributes.map((attr, idx) => (
                  <tr key={idx}>
                    <td>{attr.column_name}</td>
                    <td>
                      <textarea
                        rows="1"
                        className="auto_height"
                        value={attr.description}
                        onChange={(e) => handleDescriptionChange(e, attr)}
                        onInput={(e) => auto_height(e.target)}
                      ></textarea>
                    </td>
                    <td>{attr.data_type}</td>
                    <td>{attr.is_primary_key ? "Yes" : "No"}</td>
                    <td>{attr.is_foreign_key ? "Yes" : "No"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DataDictionary;
