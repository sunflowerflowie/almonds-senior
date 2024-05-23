import { useState, useEffect } from "react";
import { useParams, useLocation } from "react-router-dom";
import api from "../api";
import Navbar from "../components/Navbar";
import "../styles/DataDictionary.css";
import jsPDF from "jspdf";

function DataDictionary() {
  const { connection_id } = useParams(); // Extract connection_id from URL parameters
  const [dataDictionary, setDataDictionary] = useState([]); // State to hold data dictionary information
  const [saving, setSaving] = useState(false); // State to handle saving status
  const [saveButton, setSaveButton] = useState(false); // State to handle save button status
  const location = useLocation(); // Hook to get the current location
  const connectionDetails = location.state?.form; // Get connection details passed via state

  useEffect(() => {
    // Function to fetch data dictionary details
    const fetchDataDictionary = async () => {
      try {
        const tablesResponse = await api.get(`/catalog/tables/${connection_id}`);
        const newDataDictionary = await Promise.all(
          tablesResponse.data.tables.map(async (table) => {
            const attributesResponse = await api.get(
              `/catalog/attributes/${connection_id}/${table.table_name}`
            );
            return {
              tableName: table.table_name,
              attributes: attributesResponse.data.attributes.map((attr) => ({
                ...attr,
                description: attr.description,
                attribute_id: attr.attribute_id,
              })),
              error: !attributesResponse.data.attributes,
            };
          })
        );
        setDataDictionary(newDataDictionary);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchDataDictionary();
  }, [connection_id]);

  useEffect(() => {
    // Check if any attribute has a non-empty description to enable the save button
    const hasNonEmptyDescription = dataDictionary.some((table) =>
      table.attributes.some((attribute) => attribute.description.trim() !== "")
    );

    setSaveButton(hasNonEmptyDescription);
  }, [dataDictionary]);

  // Function to generate and download PDF
  const generatePDF = () => {
    const doc = new jsPDF("p", "pt", "a4");
    doc.html(document.querySelector(".data-dictionary"), {
      callback: function (pdf) {
        pdf.save("data-catalog.pdf"); // Save the PDF with the specified filename
      },
      x: 10,
      y: 10,
      width: 595.28,
      windowWidth: document.documentElement.offsetWidth,
    });
  };

  // Function to handle description change
  const handleDescriptionChange = (e, attr) => {
    const newDescription = e.target.value;

    setDataDictionary((prevData) =>
      prevData.map((table) => ({
        ...table,
        attributes: table.attributes.map((a) =>
          a.column_name === attr.column_name
            ? { ...a, description: newDescription }
            : a
        ),
      }))
    );
  };

  // Function to save changes
  const handleSaveChanges = async () => {
    setSaving(true);
    try {
      const updatedAttributes = dataDictionary.flatMap((table) =>
        table.attributes.filter((attr) => attr.description.trim() !== "")
      );

      await Promise.all(
        updatedAttributes.map((attr) => {
          const { attribute_id, description } = attr;
          return api.patch(`/catalog/update/${attribute_id}/`, {
            description: description,
          });
        })
      );
    } catch (error) {
      console.error("Error saving changes:", error);
    } finally {
      setSaving(false);
    }
  };

  // Function to adjust textarea height automatically
  const auto_height = (elem) => {
    elem.style.height = "1px";
    elem.style.height = `${elem.scrollHeight}px`;
  };

  return (
    <div className="data-dictionary">
      <Navbar /> {/* Navbar component */}
      <div className="content-container">
        <h1>Metadata</h1>
        <table className="detail">
          <tbody>
            <tr>
              <td>
                <b>Database Name:</b> {connectionDetails?.database_name}
              </td>
            </tr>
            <tr>
              <td>
                <b>Description:</b> {connectionDetails?.description}
              </td>
            </tr>
            <tr>
              <td>
                <b>Data owner:</b> {connectionDetails?.department_name}
              </td>
            </tr>
          </tbody>
        </table>
        <div className="data-dictionary-button-container">
          <button
            onClick={handleSaveChanges}
            disabled={saving || !saveButton}
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
