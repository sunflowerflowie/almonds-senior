import { useState, useEffect } from "react";
import api from "../api";
import ConnectionForm from "../components/ConnectionForm";
import "../styles/Connection.css";
import Navbar from "../components/Navbar";
import { useNavigate } from "react-router-dom";

function Connection() {
  const [forms, setForms] = useState([]);
  const [database_name, setDatabaseName] = useState("");
  const [hostname, setHostname] = useState("");
  const [port, setPort] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [description, setDescription] = useState("");
  const [platforms, setPlatforms] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState("");
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState("");
  const [departmentTags, setDepartmentTags] = useState([]);
  const [selectedDepartmentTag, setSelectedDepartmentTag] = useState("");

  let navigate = useNavigate();

  // Navigate to the data catalog page and pass the connection_id
  function handleShowTables(connection_id) {
    navigate(`/catalog/tables/${connection_id}`);
  }

  // Fetch connection forms when the component mounts
  useEffect(() => {
    getConnection();
  }, []);

  // Fetch platforms, roles, and department tags when the component mounts
  useEffect(() => {
    // Fetch Platforms
    api
      .get("/connection/platforms/")
      .then((response) => {
        setPlatforms(response.data);
        if (response.data.length > 0) {
          setSelectedPlatform(response.data[0].platform_id);
        }
      })
      .catch((error) => console.error("Error fetching platforms:", error));
    
    // Fetch Roles
    api
      .get("/connection/roles/")
      .then((response) => {
        setRoles(response.data);
        if (response.data.length > 0) {
          setSelectedRole(response.data[0].role_id);
        }
      })
      .catch((error) => console.error("Error fetching roles:", error));

    // Fetch Department Tags
    api
      .get("/connection/departments/")
      .then((response) => {
        setDepartmentTags(response.data);
        if (response.data.length > 0) {
          setSelectedDepartmentTag(response.data[0].department_id);
        }
      })
      .catch((error) => console.error("Error fetching department tags:", error));
  }, []);

  // Get the list of connection forms from the server
  const getConnection = () => {
    api
      .get("/connection/forms/")
      .then((response) => response.data)
      .then((data) => {
        setForms(data);
      })
      .catch((err) => alert(err));
  };

  // Delete a connection form by its ID
  const deleteConnection = (connection_id) => {
    api
      .delete(`/connection/forms/delete/${connection_id}/`)
      .then((res) => {
        if (res.status === 204) alert("Connection deleted!");
        else alert("Failed to delete connection.");
        getConnection(); // Refresh the list of connection forms
      })
      .catch((error) => alert(error));
  };

  // Create a new connection form
  const createConnection = (e) => {
    e.preventDefault();
    api
      .post("/connection/forms/", {
        database_name,
        hostname,
        port,
        username,
        password,
        description,
        platform: selectedPlatform,
        role: selectedRole,
        department_tag: selectedDepartmentTag,
      })
      .then((res) => {
        if (res.status === 201) alert("Connection Created!");
        else alert("Failed to create connection.");
        getConnection(); // Refresh the list of connection forms
      })
      .catch((err) => alert(err));
  };

  return (
    <div>
      <Navbar />
      <div className="content-container">
        <h2>Connection Forms</h2>
        {forms.map((form) => (
          <ConnectionForm
            form={form}
            onDelete={() => deleteConnection(form.connection_id)} // Delete the connection form
            onCatalog={() => handleShowTables(form.connection_id)} // View the data catalog for the connection
            key={form.connection_id}
          />
        ))}
      </div>
      <h2>Fill Form</h2>
      <form onSubmit={createConnection}>
        <label htmlFor="platform">Platform:</label>
        <select
          id="platform"
          value={selectedPlatform}
          onChange={(e) => setSelectedPlatform(e.target.value)}
          required
        >
          {platforms.map((platform) => (
            <option key={platform.platform_id} value={platform.platform_id}>
              {platform.platform_name}
            </option>
          ))}
        </select>
        <br />
        <label htmlFor="role">Responsibilities:</label>
        <select
          id="role"
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value)}
          required
        >
          {roles.map((role) => (
            <option key={role.role_id} value={role.role_id}>
              {role.role_name}
            </option>
          ))}
        </select>
        <br />
        <label htmlFor="department_tag">Departments:</label>
        <select
          id="department_tag"
          value={selectedDepartmentTag}
          onChange={(e) => setSelectedDepartmentTag(e.target.value)}
          required
        >
          {departmentTags.map((tag) => (
            <option key={tag.department_id} value={tag.department_id}>
              {tag.department_name}
            </option>
          ))}
        </select>
        <br />
        <label htmlFor="database_name">Database Name:</label>
        <input
          type="text"
          id="database_name"
          name="database_name"
          required
          onChange={(e) => setDatabaseName(e.target.value)}
          value={database_name}
        />
        <br />
        <label htmlFor="hostname">Hostname:</label>
        <input
          type="text"
          id="hostname"
          name="hostname"
          required
          onChange={(e) => setHostname(e.target.value)}
          value={hostname}
        />
        <br />
        <label htmlFor="port">Port:</label>
        <input
          type="number"
          id="port"
          name="port"
          required
          onChange={(e) => setPort(parseInt(e.target.value, 10))}
          value={port}
        />
        <br />
        <label htmlFor="username">Username:</label>
        <input
          type="text"
          id="username"
          name="username"
          required
          onChange={(e) => setUsername(e.target.value)}
          value={username}
        />
        <br />
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          name="password"
          required
          onChange={(e) => setPassword(e.target.value)}
          value={password}
        />
        <br />
        <label htmlFor="description">Description:</label>
        <textarea
          id="description"
          name="description"
          required
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        ></textarea>
        <br />
        <input type="submit" value="Submit"></input>
      </form>
    </div>
  );
}

export default Connection;
