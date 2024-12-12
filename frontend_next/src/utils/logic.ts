import { TASK_LENGTH } from "../constants/constants";
import { Task } from "./types";

export const getNullTask = (): Task =>
    Array.from({ length: TASK_LENGTH }, () => 0);

export const taskToString = (task: Task): string => {
    return task.join("");
};

export const stringToTask = (str: string): Task => {
    if (str.length !== TASK_LENGTH * TASK_LENGTH) {
        throw new Error("Invalid parameter");
    }

    const task: Task = [];
    for (let i = 0; i < TASK_LENGTH; ++i) {
        const val = Number(str[i]);
        if (val !== 0 && val !== 1) {
            return getNullTask();
        }
        task.push(val);
    }

    return task;
};

// export const stepBoard = (task: Task): Task => {
//     const newBoard: Board = [];

//     /**
//      * @todo [Step 1] 请在下面两条注释之间的区域填写你的代码完成该游戏的核心逻辑
//      * @note 你可以使用命令 yarn test step 来运行我们编写的单元测试与我们提供的参考实现对拍
//      */
//     // Step 1 BEGIN

//     // Step 1 END

//     return newBoard;
// };

// export const flipCell = (board: Board, i: number, j: number): Board => {
//     /**
//      * @todo [Step 3] 请在下面两条注释之间的区域填写你的代码完成切换细胞状态的任务
//      * @note 你可以使用命令 yarn test flip 来运行我们编写的单元测试以检验自己的实现
//      */
//     // Step 3 BEGIN

//     // Step 3 END

//     /**
//      * @note 该 return 语句是为了在填入缺失代码前也不至于触发 ESLint Error
//      */
//     throw new Error("This line should be unreachable.");
//     return board;
// };

// export const badFlipCell = (board: Board, i: number, j: number): Board => {
//     board[i][j] = board[i][j] === 0 ? 1 : 0;
//     return board;
// };
