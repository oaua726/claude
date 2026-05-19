"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { createPerson, deletePerson, createInteraction, deleteInteraction } from "./db";

export async function createPersonAction(formData: FormData) {
  const name = (formData.get("name") as string).trim();
  const tags = (formData.get("tags") as string).trim();
  const notes = (formData.get("notes") as string).trim();

  if (!name) return;

  const person = createPerson(name, tags, notes);
  redirect(`/persons/${person.id}`);
}

export async function deletePersonAction(id: number) {
  deletePerson(id);
  redirect("/");
}

export async function createInteractionAction(personId: number, formData: FormData) {
  const date = (formData.get("date") as string).trim();
  const content = (formData.get("content") as string).trim();
  const promises = (formData.get("promises") as string).trim();

  if (!date || !content) return;

  createInteraction(personId, date, content, promises);
  revalidatePath(`/persons/${personId}`);
}

export async function deleteInteractionAction(id: number, personId: number) {
  deleteInteraction(id);
  revalidatePath(`/persons/${personId}`);
}
