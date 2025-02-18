import { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { getCookie, setCookie } from "../utils/cookies";
import { TOKEN_COOKIE_NAME, apiBaseUrl } from "../utils/constants";
// import { ApiClient } from "../api/client";
import UserApi from "../api/user";

export function useUser() {
  // const [userId, setUserId] = useState<string>();
  const [token, setToken] = useState<string>();

  useEffect(() => {
    if (token) return;

    const _token = getCookie(TOKEN_COOKIE_NAME)
    if (_token) {
      setToken(_token);
      return;
    } else {
      UserApi.login()
        .then(data => {
          const _token = data?.token ?? "";
          setToken(_token);
          setCookie(TOKEN_COOKIE_NAME, _token);
        })
        .catch(err => {
          console.log(err);
        });
    }

    return () => {
      setToken("")
    }

  }, [token]);

  // if (!token) {
  //   const _token = getCookie(TOKEN_COOKIE_NAME)
  //   setToken(_token)
  // }


  return {
    token
  };
}
