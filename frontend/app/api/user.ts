import { ApiClient  } from "./client";

function invokeHttp(method: string, uri: string, params: object = {}, data: object = {}) {
    return new Promise((resolve, reject) => {
        ApiClient(method, "/user" + uri, params, data).then(resp => {
            resolve(resp.result)
        }).catch((error) => {
            reject(error)
        })
    })
}

export default {
    login: (data: object = {}) => {
        return invokeHttp("POST", "/login", {}, data)
    }
}