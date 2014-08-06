%% In order to pull specific aspects of the log data from the struct, you
%   can logically query the sub-struct array of sets. E.g.

log_st=readWCSTlog('some_log_file.log');
rule={'G1', 'G2', 'L1', 'L2'};
pick=1;         % create some rule criterion
stim='shape';   % create some stimulus criterion
setnum=numel(log_st.sets);
setname=cell(setnum,1);
for i=1:setnum
    setname{i}=log_st.sets(i).stats.type;
end
idx=find(~cellfun(@isempty, strfind(setname,stim)));
numidx=numel(idx);
if numidx>1
    qry_st=RecuMergeStruct(log_st.sets(idx(1)).(rule{pick}),...
                           log_st.sets(idx(2)).(rule{pick}));
    if numidx>2
        for i=3:numidx
            qry_st=RecuMergeStruct(qry_st, log_st.sets(idx(i)).(rule{pick}));
        end
    end
end