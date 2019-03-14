# Google Pub/Sub Example

## 設定環境變數

你會在本頁中，設定後續動作所需的環境變數

### 產生亂數序號

亂數產生一組序號，防止範例執行過程中出現衝突

```bash
export RND_KEY=$(cat \
    /proc/sys/kernel/random/uuid | \
    awk -F"-" '{print $5}')
```

### 設定各項環境變數名稱

執行以下指令，會設定本教程中，所有使用到的環境變數

```bash
export $(envsubst < environments | grep -v '^#' | xargs)
```

詳細的內容，您可以參考檔案[environments]或以下內容

```
# 示範用專案ID
GCP_PROJECT_ID=projectid-${RND_KEY}
# 偏好的 GCP zone
GCP_ZONE=asia-east1-a
# GKE 名稱
GCP_GKE_NAME=pubsub-k8s-name-${RND_KEY}
# Google Pub/Sub admin Service Account
GCP_PUBSUB_ADMIN=pubsub-admin-${RND_KEY}
# Google Pub/Sub topic name
GCP_PUBSUB_TOPIC=pubsub-topic-face
# Google pub/sub credential file path
#GOOGLE_APPLICATION_CREDENTIALS=/etc/google/auth/pubsub.json
# https://cloud.google.com/compute/docs/machine-types
GCP_MACHINE_TYPE=n1-standard-1

#DOCKER IMAGE
IMAGE_FACE=face:v1

```

## 建立 GCP 專案與服務

### 建立專案

```bash
gcloud projects create ${GCP_PROJECT_ID}
```

```bash
gcloud config set project ${GCP_PROJECT_ID}
```

## 建你的新專案連接計費帳戶

在進行下一步之前，您必需為您新建的專案設定計費帳戶才能進行

### 取得網址，並在網頁中開啟設定

```bash
echo "https://console.developers.google.com/project/${GCP_PROJECT_ID}/settings"
```

## 建立 kubernetes 服務

### 開啟 kubernetes API 使用權限

這指令會啟用您帳號調用 kubernetes API 的權限，過程約需等待 2分鐘

```bash
gcloud services enable container.googleapis.com
```

### 開始建立 k8s 叢集

建立 k8s 叢集, 過程約需等待 3分鐘

```bash
gcloud container clusters create \
  ${GCP_GKE_NAME} \
  --cluster-version=1.11.6-gke.2 \
  --zone ${GCP_ZONE} \
  --project ${GCP_PROJECT_ID}  \
  --machine-type ${GCP_MACHINE_TYPE} \
  --num-nodes "1"
```

### 取得k8s憑證

透過 gcloud 指令輔助，取回 k8s 憑證，並設置於 kubectl

```bash
gcloud container clusters get-credentials \
  ${GCP_GKE_NAME} \
  --zone ${GCP_ZONE} \
  --project ${GCP_PROJECT_ID} 
```


## 建立 pubsub 發佈與訂閱項目

### 建立主題 topic

```bash
gcloud pubsub topics create ${GCP_PUBSUB_TOPIC}
```

### 建立訂閱項目 subscription

```bash
gcloud pubsub subscriptions create sub-001 --topic=projects/${GCP_PROJECT_ID}/topics/${GCP_PUBSUB_TOPIC}
```
```bash
gcloud pubsub subscriptions create sub-002 --topic=projects/${GCP_PROJECT_ID}/topics/${GCP_PUBSUB_TOPIC}
```
```bash
gcloud pubsub subscriptions create sub-003 --topic=projects/${GCP_PROJECT_ID}/topics/${GCP_PUBSUB_TOPIC}
```

## 建立操作 pubsub 服務帳戶

### 建立一組新的服務帳戶

```bash
gcloud iam service-accounts create ${GCP_PUBSUB_ADMIN}
```
 
### 指定 roles/pubsub.admin 權限給予帳戶

```bash
gcloud projects add-iam-policy-binding \
  ${GCP_PROJECT_ID} \
  --member serviceAccount:${GCP_PUBSUB_ADMIN}@${GCP_PROJECT_ID}.iam.gserviceaccount.com \
  --role roles/pubsub.admin
```

### 取回認證檔

```bash
gcloud iam service-accounts keys create \
  ${GCP_PUBSUB_ADMIN}.json \
  --iam-account=${GCP_PUBSUB_ADMIN}@${GCP_PROJECT_ID}.iam.gserviceaccount.com
```

## 產生 face image

本步驟會將 face 端的程式，打包成 docker image 並上傳至 GCR

### 拷貝憑證資料

```bash
cp ${GCP_PUBSUB_ADMIN}.json ./face/pubsub.json
```

### 建立 image & push
```bash
export IMAGE_FACE=face:v1
```
```bash
cd face \
&& docker build \
  -t gcr.io/${GCP_PROJECT_ID}/${IMAGE_FACE} \
  . \
&& docker push gcr.io/${GCP_PROJECT_ID}/${IMAGE_FACE} \
&& cd ..
```


## 配置 yaml 設定，將服務啟動於 GKE

### 設定 credential file path

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/etc/google/auth/pubsub.json
```

### 啟動服務
```bash
envsubst < deploy-face.yaml | kubectl apply -f -
```

### 等待服務 ip 配發 

```bash
watch -n1 kubectl get svc
```

### 待配發 EXTERNAL-IP 
可 Ctrl + C 離開 watch


## 設定redis DATA

### 在容器中執行命令行
```bash
kubectl exec -it $(kubectl get pod --selector=app=redis --output=name  | cut -c 5-99) sh
```

### 設定 DATA
```
cat <<EOF | redis-cli --pipe
SET 001 '{"data":"iPhone Xs max 512G"}'
SET 002 '{"data":"iPhone Xs max 128G"}'
SET 003 '{"data":"iPhone Xs 256G"}'
SET 004 '{"data":"iPhone Xs 256G"}'
SET 005 '{"data":"iPhone Xs 256G"}'
SET 006 '{"data":"iPhone XR 64G"}'
SET 007 '{"data":"iPhone XR 64G"}'
SET 008 '{"data":"iPhone XR 64G"}'
SET 009 '{"data":"iPhone XR 64G"}'
SET 010 '{"data":"iPhone XR 64G"}'
SET 011 '{"data":"家樂福提貨 1000元"}'
SET 012 '{"data":"家樂福提貨 1000元"}'
SET 013 '{"data":"家樂福提貨 1000元"}'
SET 014 '{"data":"家樂福提貨 1000元"}'
SET 015 '{"data":"家樂福提貨 1000元"}'
SET 016 '{"data":"家樂福提貨 1000元"}'
SET 017 '{"data":"銘謝惠顧"}'
SET 018 '{"data":"銘謝惠顧"}'
SET 019 '{"data":"銘謝惠顧"}'
SET 020 '{"data":"銘謝惠顧"}'
EOF
```

### exit
```bash
exit
```

## 完成

最後請記得，刪除本次練習的專案，以節省費用

```bash
gcloud projects delete ${GCP_PROJECT_ID}
```

[cloud shell]: (https://console.cloud.google.com/cloudshell/editor?shellonly=true)
[environments]: (./environments)
[下載原始碼]: (http://www.google.com)


## 參考
https://cloud.google.com/pubsub/docs/quickstart-py-mac
