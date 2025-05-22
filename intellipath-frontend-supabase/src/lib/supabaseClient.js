import { createClient } from '@supabase/supabase-js';

// Vérifiez que ces valeurs ne sont pas undefined
console.log("URL:", import.meta.env.VITE_SUPABASE_URL);
console.log("Key:", import.meta.env.VITE_SUPABASE_ANON_KEY?.substring(0, 5) + "...");

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error("Variables d'environnement Supabase manquantes!");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);