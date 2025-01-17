import { gql } from "@apollo/client";
import { graphql } from "@apollo/client/react/hoc";
import { Button, Grid, LinearProgress, TextField } from "@mui/material";
import { withStyles } from "@mui/styles";
import PropTypes from "prop-types";
import React from "react";
import { v1 as uuidv1 } from "uuid";
import styles from "./Upload.scss";

class FileInput extends React.Component {
  static propTypes = {
    hint: PropTypes.string,
    onFileChange: PropTypes.func
  };

  constructor(props) {
    super(props);
    this.fileInputRef = React.createRef();
    //this.onChange = this.onChange.bind(this);
    //this.onTextInputClick = this.onTextInputClick.bind(this);
    //this.render = this.render.bind(this);
    this.state = {
      filename: "",
      file: ""
    };
  }

  handleFileChange = (evt) => {
    if (evt.target.files.length > 0) {
      const file = evt.target.files[0];
      this.props.onFileChange(file);
      this.setState({ filename: file.name, file: file });
    }
  };

  handleTextInputClick = (evt) => {
    let el = this.fileInputRef.current;
    if (el.addEventListener) {
      el.addEventListener("change", this.handleFileChange, false);
    } else {
      el.attachEvent("onchange", this.handleFileChange);
    }
    el.click();
  };

  render = () => {
    return (
      <div>
        <input
          className={styles.hidden}
          type="file"
          accept=".zip,.fmu"
          ref={this.fileInputRef}
          onInput={this.handleFileChange}
        />
        <TextField
          fullWidth={true}
          label="Select Model"
          onClick={this.handleTextInputClick}
          value={this.state.filename}
          inputProps={{
            readOnly: true,
            style: {
              cursor: "pointer"
            }
          }}
          InputLabelProps={{
            shrink: this.state.filename !== ""
          }}
        />
      </div>
    );
  };
}

class Upload extends React.Component {
  static propTypes = {
    //className: PropTypes.string,
  };
  static contextTypes = {
    authenticated: PropTypes.bool,
    user: PropTypes.object
  };

  constructor() {
    super();
    this.onModelFileChange = this.onModelFileChange.bind(this);
    this.onWeatherFileChange = this.onWeatherFileChange.bind(this);
    this.onClick = this.onClick.bind(this);

    this.state = {
      modelFile: null,
      weatherFile: null,
      uploadID: null,
      completed: 0
    };
  }

  onModelFileChange(file) {
    this.setState({ modelFile: file, completed: 0, uploadID: uuidv1() });
  }

  onWeatherFileChange(file) {
    this.setState({ weatherFile: file, completed: 0 });
  }

  onClick(onCompleteProp) {
    if (this.state.modelFile) {
      const key = `uploads/${this.state.uploadID}/${this.state.modelFile.name}`;

      const request = new XMLHttpRequest();

      const uploadComplete = () => {
        onCompleteProp(this.state.modelFile.name, this.state.uploadID);
      };

      const uploadFailed = (evt) => {
        console.log("There was an error attempting to upload the file." + evt);
      };

      const uploadCanceled = () => {
        console.log("The upload has been canceled by the user or the browser dropped the connection.");
      };

      const uploadProgress = (evt) => {
        if (evt.lengthComputable) {
          const percentComplete = Math.round((evt.loaded * 100) / evt.total);
          if (percentComplete > 100) {
            this.setState({ completed: 100 });
          } else {
            this.setState({ completed: percentComplete });
          }
        } else {
          console.log("percent: unable to compute");
        }
      };

      const uploadFile = () => {
        const response = JSON.parse(request.responseText);

        if (!response) {
          console.log("Failed to acquire upload url");
          return;
        }

        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener("progress", uploadProgress, false);
        xhr.addEventListener("load", uploadComplete, false);
        xhr.addEventListener("error", uploadFailed, false);
        xhr.addEventListener("abort", uploadCanceled, false);

        // TODO: Need to configure this on server side
        xhr.open("POST", response.url, true);

        const formData = new FormData();
        Object.entries(response.fields).forEach(([key, value]) => {
          formData.append(key, value);
        });
        formData.append("file", this.state.modelFile);

        xhr.send(formData); // multipart/form-data
      };

      const url = "/upload-url";
      const params = JSON.stringify({ name: key });
      request.open("POST", url, true);
      request.setRequestHeader("Content-type", "application/json; charset=utf-8");
      request.addEventListener("load", uploadFile, false);
      request.send(params);
    } else {
      console.log("Select file to upload");
    }
  }

  modelFileHint() {
    return this.state.modelFile ? this.state.modelFile.name : undefined;
  }

  render() {
    return (
      <div className={styles.root}>
        <LinearProgress variant="determinate" value={this.state.completed} />
        <div className={styles.center}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FileInput hint={this.modelFileHint()} onFileChange={this.onModelFileChange} />
            </Grid>
            <Grid item xs>
              <Button
                fullWidth={true}
                variant="contained"
                color="primary"
                onClick={() => {
                  this.onClick(this.props.addJobProp);
                }}>
                Upload Model
              </Button>
            </Grid>
          </Grid>
        </div>
      </div>
    );
  }
}

const localStyles = (theme) => ({
  button: {
    margin: `${theme.spacing(1)}!important`
  }
});

const withStyle = withStyles(localStyles)(Upload);

const addJobQL = gql`
  mutation addJobMutation($modelName: String!, $uploadID: String!) {
    addSite(modelName: $modelName, uploadID: $uploadID)
  }
`;

const runSimQL = gql`
  mutation runSimMutation($uploadFilename: String!, $uploadID: String!) {
    runSim(uploadFilename: $uploadFilename, uploadID: $uploadID)
  }
`;

const withRunSim = graphql(runSimQL, {
  props: ({ mutate }) => ({
    runSimProp: (uploadFilename, uploadID) => mutate({ variables: { uploadFilename, uploadID } })
  })
})(withStyle);

export default graphql(addJobQL, {
  props: ({ mutate }) => ({
    addJobProp: (modelName, uploadID) => mutate({ variables: { modelName, uploadID } })
  })
})(withRunSim);
