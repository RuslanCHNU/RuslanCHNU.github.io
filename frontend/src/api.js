import axios from "axios";

const DEV = process.env.NODE_ENV === "development";
export const api = axios.create({
  baseURL: DEV ? "http://localhost:8000/api/" : process.env.REACT_APP_API_URL,
});

api.defaults.headers.common["ngrok-skip-browser-warning"] = "69420";
