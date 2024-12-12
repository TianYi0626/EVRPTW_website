import { useState } from "react";
import { BACKEND_URL, FAILURE_PREFIX, REGISTRY_FAILED, REGISTRY_SUCCESS } from "../constants/string";
import { useRouter } from "next/router";
import { useDispatch } from "react-redux";
import Head from "next/head";
import { user } from "react-icons-kit/icomoon/user";
import { key } from "react-icons-kit/icomoon/key";
import { Icon } from "react-icons-kit";

const RegistryScreen = () => {
    const [userName, setUserName] = useState("");
    const [password, setPassword] = useState("");
    const [password2, setPassword2] = useState("");
    const dispatch = useDispatch();
    const router = useRouter();

    const registry = () => {
        if (password !== password2) {
            console.log("确认密码需与密码相同");
            alert(REGISTRY_FAILED + "，确认密码需与密码相同");
        }
        else {
            fetch(`${BACKEND_URL}/api/registry`, {
                method: "POST",
                body: JSON.stringify({
                    userName,
                    password,
                }),
            })
                .then((res) => res.json())
                .then((res) => {
                    if (Number(res.code) === 0) {
                        alert(REGISTRY_SUCCESS);
                        router.back();
                    }
                    else {
                        alert(REGISTRY_FAILED);
                    }
                })
                .catch((err) => alert(FAILURE_PREFIX + err));
        }
    };

    return (
        <>
        <Head>
            <title> Welcome to IE delivery ! </title>
        </Head>
        <div className="min-h-screen bg-base-100 items-center justify-center">
            <div className="flex flex-col items-center min-h-screen justify-center">
                <div className="card bg-accent w-96 shadow-xl">
                    <div className="card-body gap-5">
                        <h2 className="card-title my-2 py-2">注册新用户</h2>
                        <label className="input input-bordered flex items-center gap-5">
                            <Icon icon={user} size={30}></Icon>
                            <input
                                type="text"
                                className="grow p-1 m-1"
                                placeholder="用户名"
                                value={userName}
                                onChange={(e) => setUserName(e.target.value)}/>
                        </label>
                        <label className="input input-bordered flex items-center gap-5">
                            <Icon icon={key} size={30}></Icon>
                            <input
                                type="password"
                                className="p-1 m-1"
                                placeholder="密码"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}/>
                        </label>
                        <label className="input input-bordered flex items-center gap-5">
                            <Icon icon={key} size={30}></Icon>
                            <input
                                type="password"
                                className="p-1 m-1"
                                placeholder="确认密码"
                                value={password2}
                                onChange={(e) => setPassword2(e.target.value)}/>
                        </label>
                        <div className="flex text-center items-center justify-center">
                            <button
                                className="btn bg-base-100"
                                onClick={registry}
                                disabled={userName === "" || password === ""}> 确认注册 </button>
                            <button
                                className="btn bg-base-100"
                                onClick={() => router.back()}
                            >返回</button>
                        </div>
                    </div>
                </div>
            </div>
            </div>
        </>
    );
};

export default RegistryScreen;
