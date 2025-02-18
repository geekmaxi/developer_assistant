import { ApiClient  } from "./client";

function invokeHttp(method: string, uri: string, params: object = {}, data: object = {}) {
    return new Promise((resolve, reject) => {
        ApiClient(method, "/conversation" + uri, params, data).then(resp => {
            resolve(resp.result)
        }).catch((error) => {
            reject(error)
        })
    })
}

export default {
    get: (uuid: string) => {
        return invokeHttp("GET", "/", {"uuid": uuid})
    },

    search: (params: object) => {
        return invokeHttp("GET", "/search", params)
    },

    create: (data: object) => {
        return invokeHttp("POST", "/", {}, data)
    }
}