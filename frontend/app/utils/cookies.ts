import Cookies from "js-cookie";

export const getCookie = (name: string): string | undefined => {
  if (typeof window === "undefined") {
    return undefined;
  }
  return Cookies.get(name);
};

export const setCookie = (
  name: string,
  value: string,
  options?: Cookies.CookieAttributes,
): void => {
  if (typeof window === "undefined") {
    return;
  }
  if (typeof options == "undefined") {
    options = {}
  }
  options.expires == options?.expires || 365 // one year
  Cookies.set(name, value, {
    ...options
  });
};
