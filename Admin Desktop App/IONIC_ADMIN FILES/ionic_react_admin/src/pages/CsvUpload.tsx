import {
IonContent,
IonHeader,
IonPage,
IonTitle,
IonToolbar,
IonItem,
IonButton, 
IonAlert} from '@ionic/react';
import React, {useEffect, useRef, useState} from "react";
import './CsvUpload.css';
import './App.css';
import axios from "axios";




const csvUpload: React.FC = () => {
    const binUrl = "http://localhost:8000/uploadbinlist/";
    const itemUrl = "http://localhost:8000/uploaditemlist/";
    const mapURL = "http://localhost:8000/uploadskumap/";
    const [selectedFile, setSelectedFile] = useState<File>();
    const [isOpen, setIsOpen] = useState(false);
    const [results, setResults] = useState(String);
    const [uploadStat, setUploadStat] = useState(String);
    const [errMessage, setErrMessage] = useState(String);
    


    //change file variable when a file is picked from the file system
    const fileChangeHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedFile(event.target!.files![0]);
    };


    
    //Upload bin_list
    const binHandler = () => {
        const csv = new FormData();

        csv.append('file', selectedFile as File);
        try
        {
            axios.post(binUrl, csv).then(res => {
                //Create alert
                if(res.data.error != "")
                {   
                    console.log(res.data.error);
                    setUploadStat("ERROR");
                    setResults(res.data.error);
                    setErrMessage(res.data.errMsg);
                    setIsOpen(true);
                }
                else
                {
                    console.log(res.data);
                    setUploadStat("Sucessful Upload");
                    setResults("Duplications: "+ res.data.duplications+" | Insertions: "+ res.data.insertions);
                    setErrMessage(res.data.errMsg);
                    setIsOpen(true);
                }
                
            });
        } catch(error)
        {
            console.error(error);
            return(<h1>ERROR</h1>);
            
        }

    };

    //Upload sku_list
    const itemHandler = () => {
        const csv = new FormData();

        csv.append('file', selectedFile as File);
        try
        {
            axios.post(itemUrl, csv).then(res => {
                //Create alert
                if(res.data.error != "")
                {
                    setUploadStat("ERROR");
                    setResults(res.data.error);
                    setErrMessage(res.data.errMsg);
                    setIsOpen(true);
                }
                else
                {
                    console.log(res.data);
                    setUploadStat("Sucessful Upload");
                    setResults("Duplications: "+ res.data.duplications+" | Insertions: "+ res.data.insertions);
                    setErrMessage(res.data.errMsg);
                    setIsOpen(true);
                }
            });
        } catch(error)
        {
            console.error(error);
            return(<h1>ERROR</h1>);
            
        }

    };

    //upload the varius maps
    const mapHandler = () => {
        const csv = new FormData();

        csv.append('file', selectedFile as File);
        try
        {
            axios.post(mapURL, csv).then(res => {
                //Create alert
                if(res.data.error != "")
                {
                    console.log(res.data.error);
                    setUploadStat("ERROR");
                    setResults(res.data.error);
                    setErrMessage(res.data.errMsg);
                    setIsOpen(true);
                }
                else
                {
                    console.log(res.data);
                    setUploadStat("Sucessful Upload");
                    setResults("Duplications: "+ res.data.duplications+" | Insertions: "+ res.data.insertions);
                    setErrMessage(res.data.errMsg);
                    setIsOpen(true);
                }
                
            });
        } catch(error)
        {
            console.error(error);
            return(<h1>ERROR</h1>);
            
        }

    };

    return(
       <IonPage>
        <IonHeader>
            <IonToolbar>
                <IonTitle>CSV Upload</IonTitle>
                <IonButton className = "admin" href="/AdminDash">Back to Dashboard</IonButton>
            </IonToolbar>
        </IonHeader>
        <IonContent fullscreen>
            <IonItem>
                <input type="file" accept='.csv' onChange={fileChangeHandler} />
                <IonButton onClick={binHandler}>Bin List upload</IonButton>
                <IonButton onClick={itemHandler}>Sku Master upload</IonButton>
                <IonButton onClick={mapHandler}>Map upload</IonButton>
            </IonItem>
            {/*<IonButton onClick={previewHandler}>Preview</IonButton>*/}
            
            

            


            <IonAlert
                isOpen = {isOpen}
                header = {uploadStat}
                subHeader = {results}
                message = {errMessage}
                buttons={["OK"]}
                onDidDismiss={() => setIsOpen(false)}
            ></IonAlert>
        </IonContent>
        
       </IonPage>
    );
};

export default csvUpload;