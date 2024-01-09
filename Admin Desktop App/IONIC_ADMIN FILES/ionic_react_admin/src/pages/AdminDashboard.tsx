import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonButton } from '@ionic/react';
import './AdminDashboard.css';

const Dashboard: React.FC = () => {
  
  return(
     <IonPage>
      <IonHeader>
          <IonToolbar>
              <IonTitle>Admin Dashboard</IonTitle>
          </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonButton href="./Export">Export Data</IonButton>
        <IonButton href="./csvUpload">CsvUpload</IonButton>
      </IonContent>
     </IonPage>
  );
};

export default Dashboard;
