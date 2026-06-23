export interface Tag {
  id: number;
  name: string;
}

export interface Session {
  id: number;
  description: string;
  start_time: string;
  end_time: string | null;
  duration_minutes: number | null;
  is_active: boolean;
  tags: Tag[];
}
