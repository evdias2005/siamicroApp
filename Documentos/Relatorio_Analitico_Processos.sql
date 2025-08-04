-- processos pessoa física

select tl.nome linha_credito, pp.numprocesso, pp.dtprocesso, pf.nome, pj.razaosocial, tb.nome banco, pp.agencia, pp.conta, pp.numprotocolo, pf.*
from processos_processo pp, tabelas_linhacredito tl, processos_pessoafisica pf, processos_pessoajuridica pj, tabelas_banco tb 
where pp.linhacredito_id = tl.id
  AND pp.clientepf_id = pf.id
  and pp.empresa_id = pj.id
  and pp.banco_id = tb.id
order by pp.numprocesso

-- processos pessoa jurídica

select tl.nome linha_credito, pp.numprocesso, pp.dtprocesso, pj1.razaosocial, pj2.razaosocial, tb.nome banco, pp.agencia, pp.conta, pp.numprotocolo, pj1.*
from processos_processo pp, tabelas_linhacredito tl, processos_pessoajuridica pj1, processos_pessoajuridica pj2, tabelas_banco tb 
where pp.linhacredito_id = tl.id
  AND pp.clientepj_id = pj1.id
  and pp.empresa_id = pj2.id
  and pp.banco_id = tb.id
order by pp.numprocesso
