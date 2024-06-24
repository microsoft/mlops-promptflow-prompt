#!/bin/bash

azd env get-values > .env
echo "--- ✅ | Post-provisioning - populated data ---"