import React from 'react';
import ReactDOM from 'react-dom';
import ReactModal from 'react-modal';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Scan from "./Scan";
import Carton from "./Carton"
import { ChakraProvider } from "@chakra-ui/react";


ReactDOM.render(
  <Router>
  <ChakraProvider>
    <Routes>
    <Route exact path='/' element={<Scan />} />
    <Route exact path="/Carton" element={<Carton />} />
    </Routes>
    </ChakraProvider>
  </Router>,
  document.getElementById('root')
);
