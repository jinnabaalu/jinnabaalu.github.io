const fs = require("fs");
const yaml = require("yaml");

const image = "my-app-image";
const containerPort = 3000;
const hostPort = 8080;

// Create an object with the docker-compose.yml structure
const dockerCompose = {
  version: "3",
  services: {
    myApp: {
      image: image,
      ports: [`${hostPort}:${containerPort}`],
    },
  },
};

// Write the YAML to the docker-compose.yml file
fs.writeFile("docker-compose.yml", yaml.dump(dockerCompose), (err) => {
  if (err) {
    console.error(err);
    return;
  }
  console.log("docker-compose.yml file has been created.");
});
