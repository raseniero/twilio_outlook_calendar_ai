# Azure Function Example Project

This project demonstrates a simple Azure Function (HTTP trigger) in Python.

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd twilio_azure_function
```

## 2. Set Up the Local Development Environment

It is recommended to use a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Run the Project Locally

You can use the Azure Functions Core Tools to run the function locally:

```bash
func start
```

This will start the local Azure Functions runtime. The HTTP-triggered function will be available at a URL like:

```
http://localhost:7071/api/HttpExample?name=YourName
```

## 4. Test the Project

To run the unit tests, use:

```bash
PYTHONPATH=. pytest
```

Or, with unittest:

```bash
python -m unittest discover tests
```

---

## 5. Deploy to Azure Functions

### Prerequisites
- Azure account ([sign up](https://azure.com/free) if you don't have one)
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) installed
- [Azure Functions Core Tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local#install-the-azure-functions-core-tools) installed
- Python 3.8–3.11 installed

### Steps

1. **Log in to Azure:**
   ```bash
   az login
   ```
2. **Create a resource group:**
   ```bash
   az group create --name <ResourceGroupName> --location <Region>
   ```
3. **Create a storage account:**
   ```bash
   az storage account create --name <StorageAccountName> --location <Region> --resource-group <ResourceGroupName> --sku Standard_LRS
   ```
4. **Create a Function App:**
   ```bash
   az functionapp create \
     --resource-group <ResourceGroupName> \
     --consumption-plan-location <Region> \
     --runtime python \
     --runtime-version 3.11 \
     --functions-version 4 \
     --name <FunctionAppName> \
     --storage-account <StorageAccountName>
   ```
   - Replace `<FunctionAppName>` with a globally unique name.
5. **Deploy your code:**
   ```bash
   func azure functionapp publish <FunctionAppName>
   ```
6. **Test your deployed function:**
   - The output will show your function URL, e.g.:
     ```
     https://<FunctionAppName>.azurewebsites.net/api/HttpExample?name=YourName&code=<your-function-key>
     ```
   - You can find your function key in the Azure Portal under your Function App > Functions > [Your Function] > Function Keys.

For more information, see the [Azure Functions Python developer guide](https://docs.microsoft.com/azure/azure-functions/functions-reference-python).
