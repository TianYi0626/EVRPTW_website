import Head from "next/head";
import "../styles/globals.css";
import type { AppProps } from "next/app";
import store, { RootState } from "../redux/store";
import { resetAuth } from "../redux/auth";
import { useRouter } from "next/router";
import { Provider, useSelector, useDispatch } from "react-redux";
import { user } from "react-icons-kit/icomoon/user";
import { key } from "react-icons-kit/icomoon/key";
import { Icon } from "react-icons-kit";
import { useState } from "react";
import { BACKEND_URL, FAILURE_PREFIX, LOGIN_FAILED, LOGIN_SUCCESS_PREFIX } from "../constants/string";
import { setName, setToken } from "../redux/auth";

// eslint-disable-next-line @typescript-eslint/naming-convention
const App = ({ Component, pageProps }: AppProps) => {
    return (
      <>
        <Head>
          <title>Welcome to IE delivery!</title>
        </Head>
        <div className="min-h-screen bg-base-100 items-center justify-center">
          <Component {...pageProps} />
        </div>
      </>
    );
  };

export default function AppWrapper(props: AppProps) {
    return (
      <Provider store={store}>
        <App {...props} />
      </Provider>
    );
}
// const App = ({ Component, pageProps }: AppProps) => {
//     const router = useRouter();
//     const dispatch = useDispatch();
//     const auth = useSelector((state: RootState) => state.auth);
//     const [userName, setUserName] = useState("");
//     const [password, setPassword] = useState("");

//     const login = () => {
//         fetch(`${BACKEND_URL}/api/login`, {
//             method: "POST",
//             body: JSON.stringify({
//                 userName,
//                 password,
//             }),
//         })
//             .then((res) => res.json())
//             .then((res) => {
//                 if (Number(res.code) === 0) {
//                     dispatch(setToken(res.token));

//                     dispatch(setName(userName));
//                     alert(LOGIN_SUCCESS_PREFIX + userName);

//                     router.push("/main");
//                 }
//                 else {
//                     alert(LOGIN_FAILED);
//                 }
//             })
//             .catch((err) => alert(FAILURE_PREFIX + err));
//     };

//     return (
//         <>
//         <Head>
//             <title> Welcome to IE delivery ! </title>
//         </Head>
//         <div className="min-h-screen bg-base-100 items-center justify-center">
//             <div className="flex flex-col items-center min-h-screen justify-center">
//                 <div className="card bg-accent w-96 shadow-xl">
//                     <div className="card-body gap-5">
//                         <h2 className="card-title my-2 py-2">从这里开始</h2>
//                         <label className="input input-bordered flex items-center gap-5">
//                             <Icon icon={user} size={30}></Icon>
//                             <input
//                                 type="text"
//                                 className="grow p-1 m-1"
//                                 placeholder="用户名"
//                                 value={userName}
//                                 onChange={(e) => setUserName(e.target.value)}/>
//                         </label>
//                         <label className="input input-bordered flex items-center gap-5">
//                             <Icon icon={key} size={30}></Icon>
//                             <input
//                                 type="text"
//                                 className="grow p-1 m-1"
//                                 placeholder="密码"
//                                 value={password}
//                                 onChange={(e) => setPassword(e.target.value)}/>
//                         </label>
//                         <div className="flex text-center items-center justify-center">
//                             <button className="btn bg-base-100"> 登录 </button>
//                             <button className="btn bg-base-100"
//                                     onClick={() => {
//                                         console.log("Navigating to /registry");
//                                         router.push("/registry");
//                                         console.log("Current Path:", router.pathname);  // Debugging line
//                                     }}> 注册 </button>
//                         </div>
//                     </div>
//                 </div>
//             </div>
//             {/* <div style={{ padding: 12 }}>
//                 <Component {...pageProps} />
//                 {router.pathname !== "/login" && (auth.token ? (
//                     <>
//                         <p>Logged in as user name: {auth.name}</p>
//                         <button className="btn-primary" onClick={() => dispatch(resetAuth())}>
//                             Logout
//                         </button>
//                     </>
//                 ) : (
//                     <button onClick={() => router.push("/login")}>Go to login</button>
//                 ))}
//             </div> */}</div>
//         </>
//     );
// };

// // export default function AppWrapper(props: AppProps) {
// //     return (
// //         <Provider store={store}>
// //             <App {...props} />
// //         </Provider>
// //     );
// // }

// export default function AppWrapper(props: AppProps) {
//     return (
//       <Provider store={store}>
//         <App {...props} />
//       </Provider>
//     );
//   }
