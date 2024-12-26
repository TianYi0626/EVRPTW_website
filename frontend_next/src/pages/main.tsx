import { use, useEffect, useState } from "react";
import { useRouter } from "next/router";
import { BACKEND_URL } from "../constants/string";
import Image from "next/image";
import { resetAuth } from "../redux/auth";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../redux/store";

const MainPage = () => {
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();
    const dispatch = useDispatch();
    const [func, setFunc] = useState<number>(0);
    const [k, setK] = useState<number>(10);
    const [clusters, setClusters] = useState<boolean[]>(Array(20).fill(true));
    const [all, setAll] = useState<boolean>(true);
    const [none, setNone] = useState<boolean>(false);
    const name = useSelector((state: RootState) => state.auth.name);
    const [getblob, setGetblob] = useState<boolean>(false);
    const clusterList = clusters.map(b => b ? "1" : "0").join("");

    const logout = () => {
        dispatch(resetAuth());
        router.back();
    };

    const toggleClusters = (index: number) => {
        // Update a specific boolean in the array
        setClusters((prev) =>
            prev.map((value, i) => (i === index ? !value : value))
        );
    };

    const selectAll = () => {
        if (all) {
            setAll(false);
        }
        else {
            setAll(true);
            setNone(false);
            setClusters((prev) => prev.map((value, i) => (true)));
        }
    };

    const unselectAll = () => {
        if (none) {
            setNone(false);
        }
        else {
            setNone(true);
            setAll(false);
            setClusters((prev) =>
                prev.map((value, i) => (false)));
        }
    };

    const solve = () => {
        fetch(`${BACKEND_URL}/api/solve`, {
              method: "POST",
              body: JSON.stringify({
                k,
                name,
                clusters: clusterList,
            }),
            })
              .then((res) => res.json())
              .then((res) => {
                if (Number(res.code) === 0) {
                    setK(k);
                }
              })
              .catch((err) => alert(`Failed to solve: ${err}`));
    };

    useEffect(() => {
        fetch(`${BACKEND_URL}/api/location_img`, {
            method: "POST",
                body: JSON.stringify({
                    k,
                    name,
                    clusters: clusterList,
                }),
        })
        .then((res) => {
            if (!res.ok) {
                throw new Error("Failed to fetch img");
            }
            return res.blob();
        })
        .then((blob) => {
            setGetblob(true);
            const imageUrl = URL.createObjectURL(blob);
            setImageUrl(imageUrl);
            setLoading(false);
        })
        .catch((err) => {
            alert(err);
            setLoading(false);
        });
    }, [k, name, clusters, clusterList]);

    if (loading) {
        return <div>Loading...</div>;
    }

  return (
    <div className="min-h-screen bg-base-100 items-center justify-center">
        <div className="flex min-h-screen">
        <ul className="menu bg-base-200 rounded-box w-40 text-lg">
            <div className="flex flex-col h-full items-center gap-3">
            <li
                onClick={() => setFunc(0)}
                className={func === 0 ? "bg-base-100 text-black rounded-box w-36 items-center" : ""}>
                <a>展示地图</a></li>
                <li>
                <details open>
                <summary>聚类数量</summary>
                <ul className="items-center">
                    <li
                    onClick={() => setK(5)}
                    className={k === 5 ? "bg-base-100 text-black rounded-box w-20 items-center" : ""}>
                    <a>5</a></li>
                    <li
                    onClick={() => setK(10)}
                    className={k === 10 ? "bg-base-100 text-black rounded-box w-20 items-center" : ""}>
                    <a>10</a></li>
                    <li
                    onClick={() => setK(20)}
                    className={k === 20 ? "bg-base-100 text-black rounded-box w-20 items-center" : ""}>
                    <a>20</a></li>
                </ul>
                </details>
            </li>
            <li
                onClick={() => setFunc(1)}
                className={func === 1 ? "bg-base-100 text-black rounded-box w-36 items-center" : ""}>
                <a
                onClick={solve}>计算路径</a></li>
            <li
                onClick={() => setFunc(2)}
                className={func === 2 ? "bg-base-100 text-black rounded-box w-36 items-center" : ""}>
                <a>发布任务</a></li>
            <div className="flex flex-col-reverse h-full">
                <button
                    className="btn btn-error text-lg"
                    onClick={() => {
                        const logoutModal = document.getElementById("logout");
                        if (logoutModal instanceof HTMLDialogElement) {
                            logoutModal.showModal();
                        }
                        }}>
                    退出登录
                </button>
                <dialog id="logout" className="modal">
                <div className="modal-box">
                    <h3 className="font-bold text-lg">Hello!</h3>
                    <p className="py-4">是否确认退出登录？</p>
                    <div className="modal-action">
                    <form method="dialog">
                        <div className="flex gap-5">
                        <button
                            className="btn btn-accent"
                            onClick={logout}>确定</button>
                        <button className="btn">取消</button></div>
                    </form>
                    </div>
                </div>
                </dialog>
            </div></div>
        </ul>
            <div className="flex flex-col w-32">
                {clusters.slice(0, k).map((cluster, index) => (
                    <div className="form-control" key={index}>
                        <label className="cursor-pointer label">
                        <span className="label-text text-lg">区域 {index+1}</span>
                        <input
                            type="checkbox"
                            checked={cluster}
                            onChange={() => toggleClusters(index)}
                            className="checkbox checkbox-accent"
                        /></label>
                    </div>
                ))}
                <div className="form-control">
                        <label className="cursor-pointer label">
                        <span className="label-text text-lg">全选</span>
                        <input
                            type="checkbox"
                            checked={all}
                            onChange={selectAll}
                            className="checkbox checkbox-accent"
                        /></label>
                </div>
                <div className="form-control">
                        <label className="cursor-pointer label">
                        <span className="label-text text-lg">全不选</span>
                        <input
                            type="checkbox"
                            checked={none}
                            onChange={unselectAll}
                            className="checkbox checkbox-accent"
                        /></label>
                </div>
            </div>
        <div className="w-full min-h-screen">
            <div className="flex flex-col items-center justify-center">
            {imageUrl ? (
            <Image
                src={imageUrl} // The image URL from the blob
                alt="Loaded Image"
                width={1000}
                height={600}
                className="mt-4"
                priority // Optional: This can be used to prioritize loading the image
            />
            ) : (
            <p>No image found for {name}: {error} {getblob ? 1 : 2}</p>
            )}
            </div>
        </div>
      </div>
    </div>
  );
};

export default MainPage;
