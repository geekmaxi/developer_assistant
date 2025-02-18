import qs from 'qs'
import { getCookie } from '../utils/cookies';
import { TOKEN_COOKIE_NAME } from '../utils/constants';

const baseUrl = process.env.NEXT_PUBLIC_API_URL
const ApiClient = (method: string, url: string, params: object = {}, data: object = {}): Promise<any> => {
    return new Promise((resolve, reject) => {
        const token = getCookie(TOKEN_COOKIE_NAME) ?? "";
        fetch(
            baseUrl + url + "?" + qs.stringify(params),
            {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token
                },
                body: params ? JSON.stringify(data) : "{}"
            }
        ).then((response) => {
            if (response.status === 200) {
                response.json().then((data) => {
                    resolve(data)
                })
            } else {
                reject(response)
            }
        }).catch((error) => {
            reject(error)
        })
    })
}

export {
    ApiClient
}