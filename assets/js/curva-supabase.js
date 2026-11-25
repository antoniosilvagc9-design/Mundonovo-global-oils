// Public browser configuration. Authorization is enforced by Supabase RLS.
export const SUPABASE_URL = "https://hkalmvrygmkkxkuiplkz.supabase.co";
export const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_qCyO92omCB7mhxitv1R0Vg_pQnxZ73d";
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.49.4/+esm";
export const supabase = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
  auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
});
export async function acessoLiberado() {
  const {data,error} = await supabase.rpc("curva_acesso_liberado");
  if(error) throw error;
  return data === true;
}
export async function listarDocumentos() {
  if (!(await acessoLiberado())) throw new Error("Acesso bloqueado");
  const {data,error} = await supabase.from("curva_mensal_documentos").select("id,nome,ano,versao,cenario,atualizado_em").order("atualizado_em",{ascending:false});
  if(error) throw error;
  return data;
}
