import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import api from "../api";
import Navbar from "../components/Navbar";
import "../styles/DataCatalog.css";
import jsPDF from "jspdf";

function DataCatalog() {
  const [tables, setTables] = useState([]);
  const { connection_id } = useParams(); // Extract connection_id from URL parameters
  const navigate = useNavigate(); // Hook to navigate programmatically
  const location = useLocation(); // Hook to get the current location
  const connectionDetails = location.state?.form; // Get connection details passed via state

  useEffect(() => {
    // If no connection details are provided, navigate to home
    if (!connectionDetails) {
      console.log("No connection details provided, navigating to home.");
      navigate("/");
    }

    // Fetch the tables for the given connection_id
    api
      .get(`/catalog/tables/${connection_id}`)
      .then((res) => {
        if (res.data.tables) {
          setTables(res.data.tables); // Set the fetched tables in state
        } else {
          console.error("Error fetching tables:", res.data.error);
        }
      })
      .catch((error) => console.error("Error fetching tables:", error));
  }, [connection_id, connectionDetails, navigate]);

  // Function to navigate to the data dictionary page
  const navigateToDataDictionary = () => {
    navigate(`/data-dictionary/${connection_id}`);
  };

  // Function to generate and download PDF of the data catalog
  const generatePDF = () => {
    const doc = new jsPDF("p", "pt", "a4");
    doc.html(document.querySelector(".data-catalog-container"), {
      callback: function (pdf) {
        pdf.save("data-catalog.pdf"); // Save the PDF with the specified filename
      },
      x: 10,
      y: 10,
      width: 595.28,
      windowWidth: document.documentElement.offsetWidth,
    });
  };

  return (
    <div className="data-catalog-container">
      <div>
        <Navbar /> {/* Navbar component */}
      </div>
      <div className="content-container"></div>
      <header className="catalog-header">
        <h1>{connectionDetails?.database_name}</h1>
        <div className="connection-details">
          <p>
            <strong>Hostname:</strong> {connectionDetails?.hostname}
          </p>
          <p>
            <strong>Port:</strong> {connectionDetails?.port}
          </p>
          <p>
            <strong>Platform:</strong> {connectionDetails?.platform_name}
          </p>
          <p>
            <strong>Role:</strong> {connectionDetails?.role_name}
          </p>
          <p>
            <strong>Department:</strong> {connectionDetails?.department_name}
          </p>
          <p>
            <strong>Description:</strong> {connectionDetails?.description}
          </p>
        </div>
        <button onClick={generatePDF} className="data-dictionary-button">
          Export as PDF
        </button>
        <button
          onClick={navigateToDataDictionary}
          className="data-dictionary-button"
        >
          View Metadata
        </button>
      </header>
      <br />
      <h1>Tables:</h1>
      <section className="table-list">
        <ul>
          {tables.map((table, index) => (
            <li key={index}>{table.table_name}</li> // Display the list of tables
          ))}
        </ul>
      </section>
    </div>
  );
}

export default DataCatalog;
