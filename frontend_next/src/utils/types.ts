export type Task = (0 | 1)[];

/**
 * @note 用于前后端交互的 Board 数据格式
 */
export interface TaskMetaData {
    id: number;
    clients: string;
    createdAt: number;
    userName: string;
}