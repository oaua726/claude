import { notFound } from "next/navigation";
import Link from "next/link";
import { getPerson, getInteractions } from "@/lib/db";
import { deletePersonAction } from "@/lib/actions";
import InteractionForm from "@/components/InteractionForm";
import InteractionList from "@/components/InteractionList";

export default async function PersonPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const personId = Number(id);
  const person = getPerson(personId);

  if (!person) notFound();

  const interactions = getInteractions(personId);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link
            href="/"
            className="text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 mb-2 inline-block"
          >
            ← 一覧に戻る
          </Link>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            {person.name}
          </h1>
          {person.tags && (
            <div className="flex flex-wrap gap-1 mt-2">
              {person.tags.split(",").map((t) => t.trim()).filter(Boolean).map((tag) => (
                <span
                  key={tag}
                  className="text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        <form
          action={async () => {
            "use server";
            await deletePersonAction(personId);
          }}
        >
          <button
            type="submit"
            className="text-sm text-slate-400 hover:text-red-500 transition-colors mt-8"
            onClick={(e) => {
              if (!confirm(`「${person.name}」を削除しますか？`)) e.preventDefault();
            }}
          >
            削除
          </button>
        </form>
      </div>

      {person.notes && (
        <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">メモ</p>
          <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
            {person.notes}
          </p>
        </div>
      )}

      <div className="text-sm text-slate-500 dark:text-slate-400">
        やり取り記録：<span className="font-medium text-slate-700 dark:text-slate-300">{interactions.length}件</span>
      </div>

      <InteractionForm personId={personId} />

      <div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
          やり取り履歴
        </h2>
        <InteractionList interactions={interactions} personId={personId} />
      </div>
    </div>
  );
}
