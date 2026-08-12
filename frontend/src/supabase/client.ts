import { createClient } from '@supabase/supabase-js';
import type { SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

// The anon/public key is safe for the browser. The service-role key must NEVER be used here.
if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Supabase is not configured. Add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to your frontend environment variables.',
  );
}

export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);

export const BUCKET = 'design-files';