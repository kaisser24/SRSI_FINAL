import {
IonContent,
IonHeader,
IonPage,
IonToolbar,
IonItem,
IonInput,
IonButton, 
IonAlert,
IonTitle,
} from '@ionic/react';
import React, {useState} from "react";
import './Exports.css';
import './App.css';
import axios from "axios";



const Export: React.FC = () => {
    const Url = "http://localhost:8000/export/";
    const [isOpen, setIsOpen] = useState(false);
    const [results, setResults] = useState(String);
    const [downloadStat, setDownloadStat] = useState(String);
    const [errMessage, setErrMessage] = useState(String);
    const [dateX, setDateX] = useState(String);
    const [dateY, setDateY] = useState(String);
    var enteredDates: String [] = [];
    
    
    const transactionHandler = () => {
        try
        {
            enteredDates[0]=dateX;
            enteredDates[1]=dateY;
            //Key used by fastapi to identify query
            enteredDates[2] = "Transactions";
            
            axios.post(Url, {dates: enteredDates}).then(res => {
                console.log(res.data);
                if(res.data.error != "")
                {
                    setDownloadStat("Transaction Export Failed");
                    setResults(res.data.error);
                    setErrMessage(res.data.errMsg);
                    setIsOpen(true);
                }
                else
                {
                    setDownloadStat("Sucessful Export: Transactions");
                    setResults(res.data.returns+" results found");
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

    const cartonCountHandler = () => {
        try
        {
            enteredDates[0]=dateX;
            enteredDates[1]=dateY;
            //Key used by fastapi to identify query
            enteredDates[2] = "CartonCounts";
            
            axios.post(Url, {dates: enteredDates}).then(res => {
                console.log(res.data);
                if(res.data.error != "")
                {
                    setDownloadStat("Carton Counts Export Failed");
                    setResults(res.data.error);
                    setErrMessage(res.data.errMsg);
                    setIsOpen(true);
                }
                else
                {
                    setDownloadStat("Sucessful Export: Carton Counts");
                    setResults(res.data.returns+" results found");
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

    const cartonsClosedHandler = () => {
        try
        {
            enteredDates[0]=dateX;
            enteredDates[1]=dateY;
            //Key used by fastapi to identify query
            enteredDates[2] = "CartonsClosed";
            
            axios.post(Url, {dates: enteredDates}).then(res => {
                console.log(res.data);
                if(res.data.error != "")
                {
                    setDownloadStat("Cartons Closed Export Failed");
                    setResults(res.data.error);
                    setErrMessage(res.data.errMsg);
                    setIsOpen(true);
                }
                else
                {
                    setDownloadStat("Sucessful Export: Cartons Closed");
                    setResults(res.data.returns+" results found");
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
                <IonTitle>Transaction Metrics</IonTitle>
                <IonButton className = "admin" href="/AdminDash">Back to Dashboard</IonButton>
                
            </IonToolbar>
        </IonHeader>
        <IonContent fullscreen>
            <IonItem>
                <IonInput type='text' label="From:" placeholder="yyyy-mm-dd" onIonInput={(e:any) => setDateX(e.target.value)}></IonInput>
                <IonInput type='text' label="To:" placeholder="yyyy-mm-dd" onIonInput={(e:any) => setDateY(e.target.value)}></IonInput>
                <IonButton onClick={transactionHandler}>Export Transactions</IonButton>
                <IonButton onClick={cartonCountHandler}>Export Carton Item Counts</IonButton>
                <IonButton onClick={cartonsClosedHandler}>Export Cartons Closed Per Bin</IonButton>
            </IonItem>


            <IonAlert
                isOpen = {isOpen}
                header = {downloadStat}
                subHeader = {results}
                message = {errMessage}
                buttons={["OK"]}
                onDidDismiss={() => setIsOpen(false)}
            ></IonAlert>
        </IonContent>
        
       </IonPage>
    );
};

export default Export;