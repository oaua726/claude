import type { Interaction } from "@/lib/types";
import { deleteInteractionAction } from "@/lib/actions";

export default function InteractionList({
  interactions,
  personId,
}: {
  interactions: Interaction[];
  personId: number;
}) {
  if (interactions.length === 0) {
    return (
      <p className="text-center py-8 text-slate-400 dark:text-slate-500 text-sm">
        まだ記録がありません。上のフォームから追加してください。
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {interactions.map((interaction) => (
        <div
          key={interaction.id}
          className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700"
        >
          <div className="flex items-start justify-between gap-2 mb-2">
            <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
              {interaction.date}
            </span>
            <form
              action={async () => {
                "use server";
                await deleteInteractionAction(interaction.id, personId);
              }}
            >
              <button
                type="submit"
                className="text-xs text-slate-400 hover:text-red-500 transition-colors"
              >
                削除
              </button>
            </form>
          </div>

          <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
            {interaction.content}
          </p>

          {interaction.promises && (
            <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700">
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium mb-0.5">
                約束・フォローアップ
              </p>
              <p className="text-sm text-amber-700 dark:text-amber-400">
                {interaction.promises}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
