create view vw_log as 
select A.id, au.username, au.is_superuser, au.is_active, A.tabela, A.nome, A.is_deleted, A.history_date, A.history_type
from auth_user au,  
     (select thb.id, 'Banco' tabela, thb.nome , thb.is_deleted , thb.history_date , thb.history_type, thb.history_user_id
      from tabelas_historicalbanco thb 
      union
      select thc.id, 'Cidade', thc.nome , thc.is_deleted , thc.history_date , thc.history_type, thc.history_user_id 
      from tabelas_historicalcidade thc
      union
      select tho.id, 'Bairro', tho.nome , tho.is_deleted , tho.history_date , tho.history_type, tho.history_user_id
      from tabelas_historicalbairro tho
      union
      select the.id, 'EstadoCivil', the.nome , the.is_deleted , the.history_date , the.history_type, the.history_user_id
      from tabelas_historicalestadocivil the
      union
      select thf.id, 'FinalidadeCredito', thf.nome , thf.is_deleted , thf.history_date , thf.history_type, thf.history_user_id 
      from tabelas_historicalfinalidadecredito thf
      union
      select thl.id, 'LinhaCredito', thl.nome , thl.is_deleted , thl.history_date , thl.history_type, thl.history_user_id 
      from tabelas_historicallinhacredito thl
      union
      select thp.id, 'Profissao', thp.nome , thp.is_deleted , thp.history_date , thp.history_type, thp.history_user_id 
      from tabelas_historicalprofissao thp
      union      
      select thr.id, 'RamoAtividade', thr.nome , thr.is_deleted , thr.history_date , thr.history_type, thr.history_user_id 
      from tabelas_historicalramoatividade thr
      union      
      select thr1.id, 'RegimeBens', thr1.nome , thr1.is_deleted , thr1.history_date , thr1.history_type, thr1.history_user_id 
      from tabelas_historicalregimebens thr1
      union      
      select ths.id, 'SetorNegocio', ths.nome , ths.is_deleted , ths.history_date , ths.history_type, ths.history_user_id 
      from tabelas_historicalsetornegocio ths
      union      
      select thpf.id, 'PessoaFisica', thpf.nome , thpf.is_deleted , thpf.history_date , thpf.history_type, thpf.history_user_id 
      from processos_historicalpessoafisica thpf
      union      
      select thpj.id, 'PessoaJuridica', thpj.nomefantasia , thpj.is_deleted , thpj.history_date , thpj.history_type, thpj.history_user_id 
      from processos_historicalpessoajuridica thpj
      union      
      select thp.id, 'Processo', thp.numprocesso , thp.is_deleted , thp.history_date , thp.history_type, thp.history_user_id 
      from processos_historicalprocesso thp
      union      
      select tha.id, 'Avalista', cast(tha.avalista_id as text) , tha.is_deleted , tha.history_date , tha.history_type, tha.history_user_id
      from processos_historicalavalista tha
      union
      select thf2.id, 'ProcessoFinanc', cast(thf2.processo_id as text) , thf2.is_deleted , thf2.history_date , thf2.history_type, thf2.history_user_id
      from processos_historicalfinanceiro thf2
      union
      select thpr.id, 'Referencia', thpr.nome , thpr.is_deleted , thpr.history_date , thpr.history_type, thpr.history_user_id
      from processos_historicalreferencia thpr
      union
      select thn.id, 'Negociacao', cast(thn.processo_id as text) , thn.is_deleted , thn.history_date , thn.history_type, thn.history_user_id
      from processos_historicalnegociacao thn
      union
      select thp1.id, 'Parecer', cast(thp1.processo_id as text) , thp1.is_deleted , thp1.history_date , thp1.history_type, thp1.history_user_id
      from processos_historicalparecer thp1
      ) A
where au.id  = A.history_user_id

drop view vw_log

select * from vw_log



