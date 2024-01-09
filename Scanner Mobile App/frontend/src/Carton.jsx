import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import logo2 from './UA-logo.png';
import './App.css';

function CloseCarton() {
  const navigate = useNavigate();
  const [lastCarton, setLastCarton] = useState(null);

  const fetchLastCarton = async () => {
    try {
      const response = await fetch("http://localhost:8000/last_carton");
      if (response.ok) {
        const data = await response.json();
        setLastCarton(data.data);
      } else {
        console.error("Failed to fetch last carton");
      }
    } catch (error) {
      console.error("Error fetching last carton", error);
    }
  };

  useEffect(() => {
    fetchLastCarton();
  }, []);

  const formatDateTime = (timestamp) => {
    const options = { year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
    return new Date(timestamp).toLocaleString(undefined, options);
  };

  const confirmClose = async () => {
    const userConfirmed = window.confirm("Are you sure you want to close this carton?");
    if (userConfirmed) {
      try {
        const response = await fetch(`http://localhost:8000/close_carton/${lastCarton?.carton_id}`, {
          method: 'PUT',
        });
        if (response.ok) {
          navigate('/');
        } else {
          console.error("Failed to close carton");
        }
      } catch (error) {
        console.error("Error closing carton", error);
      }
    } else {
      navigate('/');
    }
  };

  return (
    <div className="App">
      <div className="black-bar">
        <img src={logo2} alt="Black Bar Image" className="black-bar-image" />
      </div>
      <br></br><br></br><br></br>
      <h1>Close Last Carton?</h1>

      <div className='cartonOutput'>
        {lastCarton ? (
          <div>
            <p>Carton ID: {lastCarton.carton_id}</p>
            <p>Bin ID: {lastCarton.bin_id}</p>
            <p>Item Count: {lastCarton.item_count}</p>
            <p>Time Open: {formatDateTime(lastCarton.time_open)}</p>
          </div>
        ) : (
          <p>No active cartons found.</p>
        )}
      </div>

      <button onClick={confirmClose} className="button">Confirm</button>
    </div>
  );
}

export default CloseCarton;
