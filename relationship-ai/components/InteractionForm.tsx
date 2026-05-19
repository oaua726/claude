"use client";

import { useRef } from "react";
import { createInteractionAction } from "@/lib/actions";

export default function InteractionForm({ personId }: { personId: number }) {
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(formData: FormData) {
    await createInteractionAction(personId, formData);
    formRef.current?.reset();
  }

  const today = new Date().toISOString().split("T")[0];

  return (
    <form ref={formRef} action={handleSubmit} className="space-y-4 p-5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
      <h3 className="font-semibold text-slate-900 dark:text-slate-100">やり取りを記録</h3>

      <div className="flex gap-3">
        <div className="flex-1">
          <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
            日付 <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            name="date"
            defaultValue={today}
            required
            className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
          話した内容 <span className="text-red-500">*</span>
        </label>
        <textarea
          name="content"
          rows={3}
          required
          placeholder="例: 新しいプロジェクトについて話した。転職を考えているとのこと。"
          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
          約束・フォローアップ
        </label>
        <input
          type="text"
          name="promises"
          placeholder="例: 来月また飲みに行く約束をした"
          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <button
        type="submit"
        className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors"
      >
        記録する
      </button>
    </form>
  );
}
