import React, { useState, useEffect } from "react";
import {
  Button,
  CssBaseline,
  TextField,
  Link,
  Paper,
  Box,
  Grid,
  Typography,
  CircularProgress,
  Modal,
  TableContainer,
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@material-ui/core";
import { DropzoneArea } from "material-ui-dropzone";
import { makeStyles } from "@material-ui/core/styles";
import _ from 'lodash';
import readXlsxFile from 'read-excel-file'

import VirtualizedData from "./VirtualizedData";
import { handleData } from './dataHandler';

function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {"Copyright © "}
      <Link color="inherit" href="https://material-ui.com/">
        Genetic Algorithm
      </Link>{" "}
      <br />
      <br />
      <a href="https://www.freepik.com/free-photos-vectors/background">
        Background vector created by starline - www.freepik.com
      </a>
    </Typography>
  );
}

const useStyles = makeStyles((theme) => ({
  root: {
    height: "100vh",
  },
  image: {
    backgroundImage: "url(bg.png)",
    backgroundRepeat: "no-repeat",
    backgroundColor:
      theme.palette.type === "light"
        ? theme.palette.grey[50]
        : theme.palette.grey[900],
    backgroundSize: "cover",
    backgroundPosition: "left",
  },
  paper: {
    margin: theme.spacing(8, 4),
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main,
  },
  form: {
    width: "100%", // Fix IE 11 issue.
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
}));

const useStyles1 = makeStyles((theme) => ({
  root: {
    flexShrink: 0,
    marginLeft: theme.spacing(2.5),
  },
}));

const MainPage = ({ history }) => {
  const [params, setParams] = useState({
    population: null,
    crossover: null,
    mutation: null,
    generation: null,
    stage1: null,
    stage2: null,
  });
  const [actualData, setActualData] = useState(null);
  const [file, setFile] = useState(null);
  const [tableData, setTableData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpened, setIsModalOpened] = useState(false);
  const [result, setResult] = useState(null);

  const classes = useStyles();
  const tableClasses = useStyles1();

  const handleSubmit = (event) => {
    event.preventDefault();
    setIsLoading(true);
    const { population, crossover, mutation, generation, stage1, stage2 } = params;
    const postParams = JSON.stringify({
      data: actualData,
      numberOfJobs: actualData.length,
      population: parseInt(population, 10),
      crossover: parseFloat(crossover),
      mutation: parseFloat(mutation),
      generation: parseInt(generation, 10),
      stages: 2,
      numberOfMachinesInStage: [parseInt(stage1, 10), parseInt(stage2, 10)]
    });
    fetch(`http://localhost:8000/genetic/`, {
      method: 'POST',
      body: postParams,
      headers: {
        "Content-Type": "application/json"
      }
    },
    ).then(res => res.json())
    .then(res => {
      setIsLoading(false);
      setIsModalOpened(true);
      setResult(res);
    })
    .catch(err => {
      setIsLoading(false);
      console.log(err);
    });
    setIsLoading(false);
  }

  const handleFileChange = (files) => {
    setFile(files[0]);
  };

  const handleChange = (event) => {
    const { target } = event;
    const { name, value } = target;
    console.log(name, value);
    setParams({ ...params, [name]: value });
  };

  const readFile = async () => {
    if (file) {
      readXlsxFile(file, { sheet: 'Data' }).then((data) => {
        let parsedData = [];
        for (let i = 1; i < data.length; i++) {
          const item = {
            weight: data[i][0],
            color: data[i][2],
            size: data[i][4]
          };
          parsedData.push(item);
        }
        const handledData = handleData(parsedData, 65);
        setTableData(data);
        setActualData(handledData);
      });
    }
  };

  useEffect(() => {
    readFile();
  },[file]);

  const isParamsEmpty = () => {
    const {
      population,
      crossover,
      mutation,
      generation,
      stage1,
      stage2,
    } = params;

    return _.isEmpty(population) || _.isEmpty(crossover) || _.isEmpty(mutation) || _.isEmpty(generation) || _.isEmpty(stage1) || _.isEmpty(stage2);
  };

  const isDataEmpty = () => {
    return _.isEmpty(tableData) || _.isEmpty(tableData[0]);
  }

  const isDisabled = isParamsEmpty() || isDataEmpty() || isLoading;

  console.log("result:", result);

  const parseArray = data => {
    return "[" + data.join(', ') + "]"
  }

  const parseNestedArray = data => {
    const inner = _.map(data, item => {
      return "[" + item.join(', ') + "]";
    });

    return "[" + inner.join(', ') + "]";
  }

  const showGantt = () => {
    history.push("/gantt", { data: result});
  }

  const renderModalBody = () => (
    <TableContainer component={Paper} style={{ position: 'absolute', width: '50%', top: '25%', left: '25%' }}>
      <Table className={tableClasses.table} aria-label="custom pagination table">
        <TableBody>
          <TableRow key="bestSol">
            <TableCell component="th" scope="row" style={{ minWidth: 200 }}>
              Best Solution
            </TableCell>
            <TableCell align="right" style={{ overflowWrap: 'anywhere' }}>{result && parseArray(result.bestSol)}</TableCell>
          </TableRow>

          <TableRow key="cMax">
            <TableCell component="th" scope="row" style={{ minWidth: 200 }}>
              Cmax
            </TableCell>
            <TableCell align="right" style={{ overflowWrap: 'anywhere' }}>{result && result.cMax}</TableCell>
          </TableRow>

          <TableRow key="machineTracker">
            <TableCell component="th" scope="row" style={{ minWidth: 200 }}>
              Machine Tracker
            </TableCell>
            <TableCell align="right" style={{ overflowWrap: 'anywhere' }}>{result && parseNestedArray(result.machineTracker)}</TableCell>
          </TableRow>

          <TableRow key="bestSol">
            <TableCell component="th" scope="row" style={{ minWidth: 200 }}>
              Running Time
            </TableCell>
            <TableCell align="right" style={{ overflowWrap: 'anywhere' }}>{`${result && result.runningTime && result.runningTime.toFixed(3)}s`}</TableCell>
          </TableRow>
          <TableRow key="gantt">
          <TableCell component="th" scope="row" style={{ minWidth: 200 }}>
            </TableCell>
            <TableCell align="right" style={{ overflowWrap: 'anywhere', margin: 0, padding: '0 10px' }}>
              <Button
                type="button"
                fullWidth
                variant="contained"
                color="primary"
                className={classes.submit}
                onClick={showGantt}
                style={{ width: '100%', marginTop: 10, marginBottom: 10 }}
              >
                Show Gantt Chart
              </Button>
            </TableCell>
          </TableRow>
            
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Grid container component="main" className={classes.root}>
      <CssBaseline />
      {!_.isEmpty(tableData) && !_.isEmpty(tableData[0]) ? (
        <Grid item xs={false} sm={4} md={6} className={classes.image}>
          <VirtualizedData data={tableData} />
        </Grid>
      ) : (
        <Grid item xs={false} sm={4} md={6} className={classes.image} />
      )}
      <Grid item xs={12} sm={8} md={6} component={Paper} elevation={6} square>
        <div className={classes.paper}>
          <Typography component="h1" variant="h5">
            Genetic Algorithm
          </Typography>
          <p>
            Import your data and set parameters according to your needs.
          </p>
          <form className={classes.form} noValidate>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={12}>
                <DropzoneArea
                  onChange={handleFileChange}
                  filesLimit={1}
                  acceptedFiles={["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  variant="outlined"
                  margin="normal"
                  required
                  fullWidth
                  id="population"
                  label="Number of Population"
                  name="population"
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  variant="outlined"
                  margin="normal"
                  required
                  fullWidth
                  name="mutation"
                  label="Probability of Mutation"
                  id="mutation"
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  variant="outlined"
                  margin="normal"
                  required
                  fullWidth
                  name="crossover"
                  label="Probability of Crossover"
                  id="crossover"
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  variant="outlined"
                  margin="normal"
                  required
                  fullWidth
                  name="generation"
                  label="Number of Generation"
                  id="generation"
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  variant="outlined"
                  margin="normal"
                  required
                  fullWidth
                  name="stage1"
                  label="Number of Machines (Stage 1)"
                  id="stage1"
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  variant="outlined"
                  margin="normal"
                  required
                  fullWidth
                  name="stage2"
                  label="Number of Machines (Stage 2)"
                  id="stage2"
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={12}>
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  color="primary"
                  className={classes.submit}
                  onClick={handleSubmit}
                  disabled={isDisabled}
                >
                  {isLoading ? <CircularProgress /> : "Run Algorithm"}
                </Button>
              </Grid>
            </Grid>

            <Box mt={5}>
              <Copyright />
            </Box>
          </form>
        </div>
      </Grid>
      <Modal
        open={isModalOpened}
        onClose={() => setIsModalOpened(false)}
        aria-labelledby="result-modal"
        aria-describedby="result-modal-desc"
      >
        {renderModalBody()}
      </Modal>
    </Grid>
  );
}

export default MainPage;