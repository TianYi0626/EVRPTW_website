import { useRouter } from "next/router";
import { useEffect, useRef, useState } from "react";
import { CREATE_SUCCESS, FAILURE_PREFIX, LOGIN_REQUIRED, UPDATE_SUCCESS } from "../constants/string";
import { getNullTask, taskToString, stringToTask } from "../utils/logic";
import { NetworkError, NetworkErrorType, request } from "../utils/network";
import { RootState } from "../redux/store";
import { resetTaskCache, setTaskCache } from "../redux/task";
import { useSelector, useDispatch } from "react-redux";

const MainScreen = () => {
    /**
     * @todo [Step 3] 请在下述一处代码缺失部分填写合适的代码，使得棋盘状态正确切换且计时器资源分配、释放合理
     */
    const taskCache = useSelector((state: RootState) => state.task.task);
    const userName = useSelector((state: RootState) => state.auth.name);

    const dispatch = useDispatch();

    const [id, setId] = useState<undefined | number>(undefined);
    const [initTask, setInitTask] = useState(getNullTask());
    const [task, setTask] = useState(taskCache);
    const [autoPlay, setAutoPlay] = useState(false);
    const [recordUserName, setRecordUserName] = useState("");
    const [refreshing, setRefreshing] = useState(false);

    const timerRef = useRef<undefined | NodeJS.Timeout>(undefined);

    const router = useRouter();
    const query = router.query;

    useEffect(() => {
        if (!router.isReady) {
            return;
        }
        if (router.query.id === undefined) {
            // @todo 这里需要考虑是否需要加载缓存
            setId(undefined);
            return;
        }
        if (!/^[0-9]+$/.test(router.query.id as string)) {
            router.replace("/");
            return;
        }

        setRefreshing(true);
        setId(Number(router.query.id));
        request(`/api/boards/${router.query.id}`, "GET", false)
            .then((res) => {
                const fetchedTask = stringToTask(res.board);

                setTask(fetchedTask);
                setInitTask(fetchedTask);
                setRecordUserName(res.userName);
            })
            .catch((err) => {
                alert(FAILURE_PREFIX + err);
                router.push("/");
            })
            .finally(() => setRefreshing(false));
    }, [router, query]);

    useEffect(() => () => {
        clearInterval(timerRef.current);
    }, []);

    useEffect(() => {
        if (id === undefined) {
            dispatch(resetTaskCache());
        }

        return () => {
            if (id === undefined) {
                dispatch(setTaskCache(task));
            }
        };
    }, [task, id, dispatch]);

    const switchAutoPlay = () => {
        // Step 3 BEGIN

        // Step 3 END
    };

    const ExecuteTask = () => {
        request(
            "/api/task",
            "POST",
            true,
            {
                userName,
                task: taskToString(task),
            }
        )
            .then((res) => alert(res.isCreate ? CREATE_SUCCESS : UPDATE_SUCCESS))
            .catch((err) => {
                if (
                    err instanceof NetworkError &&
                    err.type === NetworkErrorType.UNAUTHORIZED
                ) {
                    alert(LOGIN_REQUIRED);
                    router.push("/login");
                }
                else {
                    alert(FAILURE_PREFIX + err);
                }
            });
    };

    return refreshing ? (
        <p> Loading... </p>
    ) : (
        <>
            {id === undefined ? (
                <h4> Free Mode </h4>
            ) : (
                <h4> Replay Mode, Board ID: {id}, Author: {recordUserName} </h4>
            )}
            <div style={{ display: "flex", flexDirection: "column" }}>
                <div style={{ display: "flex", flexDirection: "row" }}>
                    <button onClick={() => setTask(getNullTask())} disabled={autoPlay}>
                        Clear the board
                    </button>
                    {id !== undefined && (
                        <button onClick={() => setTask(initTask)} disabled={autoPlay}>
                            Undo all changes
                        </button>
                    )}
                    <button onClick={switchAutoPlay}>
                        {autoPlay ? "Stop" : "Start"} auto play
                    </button>
                </div>
                <div style={{ display: "flex", flexDirection: "row" }}>
                    <button onClick={() => router.push("/list")}>
                        Go to full list
                    </button>
                    {id !== undefined && (
                        <button onClick={() => router.push("/")}>
                            Go back to free mode
                        </button>
                    )}
                </div>
            </div>
        </>
    );
};

export default MainScreen;
