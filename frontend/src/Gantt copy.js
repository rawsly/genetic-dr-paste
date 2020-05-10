import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import _ from "lodash";
import moment from "moment";
import TimeLine from "react-gantt-timeline";

const Gantt = ({ location }) => {
  const { data } = location.state;

  data.machineTracker.sort(
    (function (index) {
      return function (a, b) {
        return a[index] === b[index] ? 0 : a[index] < b[index] ? -1 : 1;
      };
    })(0)
  );

  const [ganttData, setGanttData] = useState(null);

  useEffect(() => {
    handleMachineTracker();
  }, []);

  const handleMachineTracker = () => {
    const firstStage = [];
    const secondStage = [];
    _.map(data.machineTracker, (item, index) => {
      if (item[2] === 0) {
        firstStage.push(item);
      } else {
        secondStage.push(item);
      }
    });

    const ganttData = [];
    _.map(firstStage, (item, index) => {
      const firstItem = {
        id: index,
        start: moment().add(item[0], 'hours'),
        end: moment().add(item[1], 'hours'),
        name: `Machine: ${item[3] + 1} / Job: ${item[4] + 1} / Stage: ${item[2] + 1}`,
        color: item[2] === 0 ? '#8ED5A6' : '#FEA195'
      };
      ganttData.push(firstItem);
    });

    _.map(secondStage, (item, index) => {
      const secondItem = {
        id: index + firstStage.length,
        start: moment().add(item[0], 'hours'),
        end: moment().add(item[1], 'hours'),
        name: `Machine: ${item[3] + 1} / Job: ${item[4] + 1} / Stage: ${item[2] + 1}`,
        color: item[2] === 0 ? '#8ED5A6' : '#FEA195'
      };
      ganttData.push(secondItem);
    });

    setGanttData(ganttData);
    console.log(ganttData);

    return ganttData;
  };

  return ganttData && (
    <TimeLine data={ganttData} />
  );
};

Gantt.propTypes = {
  location: PropTypes.shape({}).isRequired
};

export default Gantt;
