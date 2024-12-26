// pages/index.tsx
import { useState } from "react";
import { useRouter } from "next/router";
import { Icon } from "react-icons-kit";
import { user, key } from "react-icons-kit/icomoon";
import { useDispatch } from "react-redux";
import { setToken, setName } from "../redux/auth";
import { BACKEND_URL, LOGIN_SUCCESS_PREFIX, LOGIN_FAILED } from "../constants/string";

const HomePage = () => {
  const router = useRouter();
  const dispatch = useDispatch();
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");

  const login = () => {
    fetch(`${BACKEND_URL}/api/login`, {
      method: "POST",
      body: JSON.stringify({ userName, password }),
    })
      .then((res) => res.json())
      .then((res) => {
        if (Number(res.code) === 0) {
          dispatch(setToken(res.token));
          dispatch(setName(res.name));
          alert(LOGIN_SUCCESS_PREFIX + userName);
          router.push("/main");
        }
        else {
          if (Number(res.code) === 1) {
            alert(LOGIN_FAILED+"：用户不存在");
          }
          else {
            if (Number(res.code) === 2) {
              alert(LOGIN_FAILED+"：密码错误");
            }
          }
        }
      })
      .catch((err) => alert(`Failed to login: ${err}`));
  };

  return (
    <div className="min-h-screen bg-base-100 items-center justify-center">
      <div className="flex flex-col items-center min-h-screen justify-center">
        <div className="card bg-accent w-96 shadow-xl">
          <div className="card-body gap-5">
            <h2 className="card-title my-2 py-2">从这里开始</h2>
            <label className="input input-bordered flex items-center gap-5">
              <Icon icon={user} size={30} />
              <input
                type="text"
                className="grow p-1 m-1"
                placeholder="用户名"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
              />
            </label>
            <label className="input input-bordered flex items-center gap-5">
              <Icon icon={key} size={30} />
              <input
                type="password"
                className="grow p-1 m-1"
                placeholder="密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>
            <div className="flex text-center items-center justify-center">
              <button className="btn bg-base-100" onClick={login}>
                登录
              </button>
              <button
                className="btn bg-base-100"
                onClick={() => router.push("/registry")}
              >
                注册
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
