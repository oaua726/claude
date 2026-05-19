import Link from "next/link";
import { getPersons } from "@/lib/db";

export default function Home() {
  const persons = getPersons();

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-6">
        人物一覧
      </h1>

      {persons.length === 0 ? (
        <div className="text-center py-16 text-slate-500 dark:text-slate-400">
          <p className="text-4xl mb-4">👥</p>
          <p className="text-lg mb-2">まだ人物が登録されていません</p>
          <p className="text-sm mb-6">会った人や関わりのある人を登録して、関係を記録しましょう</p>
          <Link
            href="/persons/new"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
          >
            + 最初の人物を追加
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {persons.map((person) => (
            <Link
              key={person.id}
              href={`/persons/${person.id}`}
              className="block p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-sm transition-all"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h2 className="font-semibold text-slate-900 dark:text-slate-100 truncate">
                    {person.name}
                  </h2>
                  {person.tags && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {person.tags.split(",").map((tag) => tag.trim()).filter(Boolean).map((tag) => (
                        <span
                          key={tag}
                          className="text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  {person.notes && (
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 line-clamp-1">
                      {person.notes}
                    </p>
                  )}
                </div>
                <span className="text-slate-300 dark:text-slate-600 text-lg">›</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
