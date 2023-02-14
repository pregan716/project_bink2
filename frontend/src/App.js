import "./App.css";
import Layout from "./components/layout/Layout";
import React, { useContext } from "react";
import { Route, Routes } from 'react-router-dom';
import PlayerPropsOverUnder from "./pages/PlayerPropsOverUnder";
import AuthPage from "./pages/AuthPage";
import AuthContext from "./store/auth-context";
import WatchlistPage from "./pages/WatchlistPage";
import MyBetsPage from "./pages/MyBetsPage";
import PlayerPropsYesNo from "./pages/PlayerPropsYesNo"
import TeamPropsOverUnder from "./pages/TeamPropsOverUnder"
import TeamPropsYesNo from "./pages/TeamPropsYesNo"
import HomePage from "./pages/HomePage";



function App() {
  const authCtx = useContext(AuthContext);
  
  return (
    <Layout>
      <Routes>
        <Route path='/' exact element={<HomePage />} />
        <Route path='/PlayerPropsOverUnder' exact element={<PlayerPropsOverUnder />} />
        <Route path='/PlayerPropsYesNo' exact element={<PlayerPropsYesNo />} />
        <Route path='/TeamPropsOverUnder' exact element={<TeamPropsOverUnder />} />
        <Route path='/TeamPropsYesNo' exact element={<TeamPropsYesNo />} />
        {!authCtx.isLoggedIn && (
          <Route path='/auth' exact element={<AuthPage />} />
        )}
        {authCtx.isLoggedIn && (
          <React.Fragment>
            <Route path='/watchlist' exact element={<WatchlistPage />} />
            <Route path='/mybets' exact element={<MyBetsPage />} />
          </React.Fragment>
        )}
      </Routes>
    </Layout>
  );
}

export default App;
