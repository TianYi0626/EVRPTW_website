import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { Task } from "../utils/types";
import { getNullTask } from "../utils/logic";

interface TaskState {
    task: Task;
}

const initialState: TaskState = {
    task: getNullTask(),
};

export const taskSlice = createSlice({
    name: "task",
    initialState,
    reducers: {
        setTaskCache: (state, action: PayloadAction<Task>) => {
            state.task = action.payload;
        },
        resetTaskCache: (state) => {
            state.task = getNullTask();
        },
    },
});

export const { setTaskCache, resetTaskCache } = taskSlice.actions;
export default taskSlice.reducer;
