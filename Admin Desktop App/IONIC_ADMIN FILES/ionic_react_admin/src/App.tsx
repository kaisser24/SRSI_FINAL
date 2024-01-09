import { Redirect, Route } from 'react-router-dom';
import {
  IonApp,
  IonIcon,
  IonLabel,
  IonRouterOutlet,
  IonTabBar,
  IonTabButton,
  IonTabs,
  setupIonicReact
} from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
import AdminDashboard from './pages/AdminDashboard';
import AdminDash from './pages/AdminDashboard';
import CsvUpload from './pages/CsvUpload'
import Exports from './pages/Exports';
//import Cartons from './pages/CartonsDownload';


/* Core CSS required for Ionic components to work properly */
import '@ionic/react/css/core.css';

/* Basic CSS for apps built with Ionic */
import '@ionic/react/css/normalize.css';
import '@ionic/react/css/structure.css';
import '@ionic/react/css/typography.css';

/* Theme variables */
import './theme/variables.css';

setupIonicReact();

const App: React.FC = () => (
  <IonApp>
    <IonReactRouter>
    <IonRouterOutlet>
          <Route exact path="/AdminDashboard">
            <AdminDashboard />
          </Route>
          <Route exact path="/csvUpload">
            <CsvUpload />
          </Route>
          <Route exact path="/">
            <Redirect to="/AdminDash"/>
          </Route>
          <Route exact path = "/AdminDash">
            <AdminDash />
          </Route>
          <Route exact path = "/Export">
            <Exports/>
          </Route>
        </IonRouterOutlet>
    </IonReactRouter>
  </IonApp>
);

export default App;
