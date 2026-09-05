import { statusLabels, stageLabels, type Stage, type Status } from "@/types";
export function StatusBadge({ value, kind = "status" }: { value: Status | Stage; kind?: "status" | "stage" }) {
  return <span className={`badge badge-${value}`}>{kind === "status" ? statusLabels[value as Status] : stageLabels[value as Stage]}</span>;
}
