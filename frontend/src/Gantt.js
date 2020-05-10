import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import _ from "lodash";
import moment from "moment";
import Chart from 'react-google-charts';

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
      const start = moment().add(item[0], 'minutes');
      const end = moment().add(item[1], 'minutes');
      const actualStart = moment().add(item[0], 'minutes');
      const actualEnd = moment().add(item[1], 'minutes');
      const firstItem = [
        `${index}`,
        `Machine: ${item[3] + 1} / Job: ${item[4] + 1} / Stage: ${item[2] + 1}`,
        `${item[4] + 1}`,
        start.toDate(),
        end.toDate(),
        actualEnd.diff(actualStart, 'minutes'),
        100,
        null
      ]
      ganttData.push(firstItem);
    });

    _.map(secondStage, (item, index) => {
      const start = moment().add(item[0], 'minutes');
      const end = moment().add(item[1], 'minutes')
      const actualStart = moment().add(item[0], 'minutes');
      const actualEnd = moment().add(item[1], 'minutes');
      const secondItem = [
        `${index + firstStage.length}`,
        `Machine: ${item[3] + 1} / Job: ${item[4] + 1} / Stage: ${item[2] + 1}`,
        `${item[4] + 1}`,
        start.toDate(),
        end.toDate(),
        actualEnd.diff(actualStart, 'minutes'),
        100,
        null
      ]
      ganttData.push(secondItem);
    });

    setGanttData(ganttData);
    console.log(ganttData);
    
    return ganttData;
  };

  return ganttData && (
    <Chart
      width="100%"
      height={42 * ganttData.length + 50}
      chartType="Gantt"
      loader={<div>Loading chart...</div>}
      data={[
        [
          { type: 'string', label: 'Task ID' },
          { type: 'string', label: 'Task Name' },
          { type: 'string', label: 'Job' },
          { type: 'date', label: 'Start Date' },
          { type: 'date', label: 'End Date' },
          { type: 'number', label: 'Duration' },
          { type: 'number', label: 'Percent Complete' },
          { type: 'string', label: 'Dependencies' },
        ],
        ...ganttData
      ]}
    />
  );
};

Gantt.propTypes = {
  location: PropTypes.shape({}).isRequired
};

export default Gantt;
