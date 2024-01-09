import React, { useEffect, useState } from "react";
import { BrowserMultiFormatReader } from "@zxing/library";
import { useNavigate } from "react-router-dom";
import logo2 from "./UA-logo.png";
import "./App.css";

const ScansContext = React.createContext({
  scans: [],
  fetchScans: () => {},
});

function AddScan() {
  const navigate = useNavigate();
  const [item, setItem] = React.useState("");
  const { fetchScans } = React.useContext(ScansContext);

  const handleInput = (event) => {
    setItem(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const newScan = {
      scan_num: item,
    };

    try {
      const response = await fetch("http://localhost:8000/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newScan),
      });

      if (!response.ok) {
        throw new Error(
          `Failed to add scan. Server returned ${response.status}`
        );
      }

      const responseData = await response.json();

      if (responseData.data) {
        console.log("Scan added:", responseData.data.message);

        const binId = responseData.data.scan.bin_id;

        if (binId) {
          document.getElementById("result").textContent = `${binId}`;
        } else {
          console.error("Bin ID not found for SKU:", responseData.data.scan.scan_num);
          document.getElementById("result").textContent = "Bin ID not found";
        }

        fetchScans();
        setItem("");
      } else if (responseData.sku_not_found) {
        console.error("No matching entry found for SKU:", item);
        document.getElementById("result").textContent = responseData.error;
      } else {
        console.error("Unexpected response format:", responseData);
        document.getElementById("result").textContent =
          "Unexpected response format";
      }
    } catch (error) {
      console.error("Error adding scan", error);
    }
  };
}

export default function Scans() {
  const [scans, setScans] = useState([]);
  const navigate = useNavigate();

  function goCarton(event) {
    event.preventDefault();
    navigate("/Carton");
  }

  const fetchScans = async () => {
    try {
      const response = await fetch("http://localhost:8000/scan");
      if (response.ok) {
        const scansData = await response.json();
        setScans(scansData.data);
      } else {
        console.error("Failed to fetch scans");
      }
    } catch (error) {
      console.error("Error fetching scans", error);
    }
  };

  useEffect(() => {
    fetchScans();
  }, []);

  useEffect(() => {
    const initializeScanner = async () => {
      const codeReader = new BrowserMultiFormatReader();
      console.log("ZXing code reader initialized");

      try {
        const videoInputDevices = await codeReader.listVideoInputDevices();
        const sourceSelect = document.getElementById("sourceSelect");
        let selectedDeviceId = videoInputDevices[0].deviceId;

        if (videoInputDevices.length >= 1) {
          videoInputDevices.forEach((element) => {
            const sourceOption = document.createElement("option");
            sourceOption.text = element.label;
            sourceOption.value = element.deviceId;
          });

          // sourceSelect.onchange = () => {
          //   selectedDeviceId = sourceSelect.value;
          // };

          // const sourceSelectPanel = document.getElementById('sourceSelectPanel');
          // sourceSelectPanel.style.display = 'block';
        }

        const startContinuousDecode = () => {
          codeReader.decodeFromVideoDevice(
            selectedDeviceId,
            "video",
            handleResult
          );
          console.log(`Started continuous decode from camera with id ${selectedDeviceId}`);
        };

        const handleResult = async (result, err) => {
          document.getElementById("result").textContent = "";
          try {
            if (result) {
              codeReader.reset();
              const newScan = {
                scan_num: result.text,
              };

              const response = await fetch("http://localhost:8000/scan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newScan),
              });

              if (!response.ok) {
                throw new Error(
                  `Failed to add scan. Server returned ${response.status}`
                );
              }

              const responseData = await response.json();

              if (responseData.data) {
                console.log("Scan added:", responseData.data.message);
                const binId = responseData.data.scan.bin_id;

                if (binId) {
                  document.getElementById("result").textContent = `${binId}`;
                } else {
                  console.error(
                    "Bin ID not found for SKU:",
                    responseData.data.scan.scan_num
                  );
                  document.getElementById("result").textContent =
                    "Bin ID not found";
                }
                fetchScans();
              } else {
                console.error("Unexpected response format:", responseData);
                document.getElementById("result").textContent = responseData.error;
              }

              console.log(result);
            }
          } catch (error) {
            console.error("Error handling barcode scan:", error);
          }
        };
        document.getElementById("startButton")?.addEventListener("click", startContinuousDecode);
        document.getElementById("resetButton")?.addEventListener("click", () => {
          codeReader.reset();
          document.getElementById("result").textContent = "";
          console.log("Reset.");
        });
      } catch (err) {
        console.error(err);
      }
    };

    initializeScanner();
  }, []);

  return (
    <div className="App">
      <div className="black-bar">
        <img src={logo2} alt="Black Bar Image" className="black-bar-image" />
        <button onClick={goCarton} className="logout-button">
          Close Carton
        </button>
      </div>
      <br></br>
      <main className="wrapper" style={{ paddingTop: "2em" }}>
        <section className="container" id="demo-content">
          <div>
            <video id="video" width="300" height="200" style={{ border: "1px solid gray" }}></video>
          </div>

          <div className="center">
            <a className="button" id="startButton">SCAN</a>
          </div>

          {/* CODE FOR SELECTING VIDEO SOURCE
          <div id="sourceSelectPanel" style={{ display: 'none' }}>
            <label htmlFor="sourceSelect">Change video source:</label>
            <select id="sourceSelect" style={{ maxWidth: '400px', accentColor: 'black'}}></select>
          </div> */}

          <label>BIN NUMBER:</label>
          <pre>
            <code id="result"></code>
          </pre>
        </section>
      </main>
    </div>
  );
}
