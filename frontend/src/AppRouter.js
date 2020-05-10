import React from 'react';
import { Switch, Route } from 'react-router-dom';
import MainPage from './MainPage';
import Gantt from './Gantt';

const AppRouter = props => (
  <Switch>
    <Route exact path="/" component={MainPage} />
    <Route exact path="/gantt" component={Gantt} />
  </Switch>
);

export default AppRouter;
