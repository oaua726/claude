export type Person = {
  id: number;
  name: string;
  tags: string;
  notes: string;
  created_at: string;
};

export type Interaction = {
  id: number;
  person_id: number;
  date: string;
  content: string;
  promises: string;
  created_at: string;
};
