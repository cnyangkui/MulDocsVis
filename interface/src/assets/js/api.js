import axios from 'axios'
import qs from 'qs'

let baseURL = 'http://127.0.0.1:8000/api';
axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;
// axios.defaults.headers.post['Content-Type'] = 'application/json' //'application/x-www-form-urlencoded';

export function getProj() {
    return axios.get('/proj/');
}

function getRequest(apiPath, params, successCallback, errorCallback) {
    let url = baseURL + apiPath
    let req = axios.get(url, {
        params: params,
        paramsSerializer: params => {
            return qs.stringify(params, { indices: false })
        }
    })
    thenResponse(req, successCallback, errorCallback)
}
function postRequest(apiPath, params, successCallback, errorCallback) {
    let url = baseURL + apiPath
    let req = axios.post(url, qs.stringify(params, { indices: false }))
    thenResponse(req, successCallback, errorCallback)
}

function putRequest(apiPath, params, successCallback, errorCallback) {
    let url = baseURL + apiPath
    let req = axios.put(url, qs.stringify(params, { indices: false }))
    thenResponse(req, successCallback, errorCallback)
}

function deleteRequest(apiPath, params, successCallback, errorCallback) {
    let url = baseURL + apiPath
    let req = axios.delete(url, {
        params: params,
        paramsSerializer: params => {
            return qs.stringify(params, { indices: false })
        }
    })
    thenResponse(req, successCallback, errorCallback)
}

/**
 * 请求结果处理
 * @param axiosRequest
 * @param successCallback
 * @param errorCallback
 */
function thenResponse(axiosRequest, successCallback, errorCallback) {
    axiosRequest.then((res) => {
        if (res.status === 200) {
            res = res.data
            if (res.code === 0) {
                if (successCallback) successCallback(res)
            } else {
                if (errorCallback) errorCallback(res.code, res.msg)
            }
        }
    }).catch((error) => {
        if (errorCallback) errorCallback(-1, error.message)
    })
}
export { getRequest, postRequest, putRequest, deleteRequest }