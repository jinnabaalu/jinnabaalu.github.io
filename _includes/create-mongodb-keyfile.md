### Create keyfile for authentication

- Create folder for storing the keyfile 

    `$ mkdir -p docker-mongo/keyfile-mac && cd docker-mongo//keyfile-mac`

- Create the keyfile with the `openssl` and save as `mongoKeyFileMac` with the following commands 

    `$ openssl rand -base64 741 >> mongoKeyFileMac`

    `$ chmod 400 mongoKeyFileMac`

> Note: chmod to change file permissions to provide read permissions for the file owner.

To know more about the keyfile creation and permisions based on the Operating system read about [create keyfile](https://jinnabalu.com/Create-keyfile-for-MongoDB)