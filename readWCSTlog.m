function data=readWCSTlog( fname )
% READWCSTLOG takes a filename and parses the given log file.
    % Read file
    if exist(fname, 'file')
        fid = fopen(fname);
        data = textscan(fid, '%s%s%s', 'Delimiter', '\t');
    else
        myReport( [fname ' does not exist. Abort'] );
        return;
    end
    %% extract time and triggers
    time = cellfun(@str2double, data{1} );
    trig = data{3};
    % trim data sets
    thr=find(~cellfun(@isempty, strfind(trig, '------------')));
    time(1:thr(2))=[];
    head=trig(1:thr(1)-1);
    trig(1:thr(2))=[];
    if ~isempty(strfind(fname, 'pilot'))
        deck=find(~cellfun(@isempty, strfind(trig, 'Using deck')));
        trig(deck)=[];
        time(deck)=[];
    end
    
    %% get header info
    data=struct;
    data.subj = head{1}(10:end);
    data.date = datevec(head{2}(6:end));
    data.age = str2double(head{3}(6:end));
    data.group = head{4}(8:end);
    % get full dataset stats
    data.stats = getstats(time, trig, 'All Trials');
    
    %% Get logicals for each category of interest
    cue_l=~cellfun(@isempty, strfind(trig,'CUE'));
    stm_l=~cellfun(@isempty, strfind(trig,'STIM'));
    tgt_l=~cellfun(@isempty, strfind(trig,'TGT'));
    rsp_l=~cellfun(@isempty, strfind(trig,'RESP'));
%     fdb_l=~cellfun(@isempty, strfind(trig,'FEEDB'));
    cues=time(cue_l);
    stims=trig(stm_l);
    trgts=trig(tgt_l);
    resps=trig(rsp_l);
%     feedb=trig(fdb_l);
    
    %% get rules
    rule_ttl={'G1', 'G2', 'L1', 'L2'};
%     rules=struct;
    for i=1:4
        data.rules.(rule_ttl{i}) = getstats(...
            time(~cellfun(@isempty, strfind(stims,rule_ttl{i}))),...
            trig(~cellfun(@isempty, strfind(stims,rule_ttl{i}))),...
            rule_ttl{i});
    end

    %% get stimulus blocks
    blockidx=find(~cellfun(@isempty, strfind(trig, 'Running set')));
    blockidx=[blockidx; numel(time)];
%     blocks=struct;
    for i=1:numel(blockidx)-1
        blocks(i) = getstats(time(blockidx(idx):blockidx(idx+1)-1),...
                            trig(blockidx(idx):blockidx(idx+1)-1),...
                            trig{blockidx(idx)}(13:end-5)); %#ok<AGROW>
    end
    data.blocks=blocks;
    data.errate=mean([data.blocks.errate]);
end

function stats=getstats(time, trig, type)
    stats=struct;

    cue_l=~cellfun(@isempty, strfind(trig,'CUE'));
    stm_l=~cellfun(@isempty, strfind(trig,'STIM'));
    tgt_l=~cellfun(@isempty, strfind(trig,'TGT'));
    rsp_l=~cellfun(@isempty, strfind(trig,'RESP'));
%     fdb_l=~cellfun(@isempty, strfind(trig,'FEEDB'));
    cues=time(cue_l);
    stims=trig(stm_l);
    trgts=trig(tgt_l);
    resps=trig(rsp_l);
%     feedb=trig(fdb_l);
    
    rG1=~cellfun(@isempty, strfind(stims,'G1'));
    rG2=~cellfun(@isempty, strfind(stims,'G2'));
    rL1=~cellfun(@isempty, strfind(stims,'L1'));
    rL2=~cellfun(@isempty, strfind(stims,'L2'));
    
    diff=[5; double(rG1(1:end-1))];
    ruleChg=abs(diff-rG1);
    diff=[5; double(rG2(1:end-1))];
    ruleChg=ruleChg+abs(diff-rG2);
    diff=[5; double(rL1(1:end-1))];
    ruleChg=ruleChg+abs(diff-rL1);
    diff=[5; double(rL2(1:end-1))];
    ruleChg=logical(ruleChg+abs(diff-rL2));
    
    trials=numel(stims);
    rts=time(rsp_l) - time(tgt_l); % response time measures lag from target presenation to response
    rt=mean(rts);
    rtv=var(rts);
    err=cellfun(@isempty, strfind(resps,'RESP   0'));
    errate=sum(~err)*100/trials;
    errate_unforced=sum(~err)*100/(trials-sum(ruleChg));
    
    targets=NaN(4,trials);
    refcards=NaN(4,trials,4);
    for i=1:trials
        targets(:,i)=cell2mat(textscan(stims{i}(8:18),'%d','Delimiter',','));
        refparts=textscan(trgts{i}(8:end),'%s%s%s%s','Delimiter',';');
        for j=1:4
            refcards(:,i,j)=cell2mat(textscan(refparts{j}{1},'%d','Delimiter',','));
        end
    end
    clear refparts
%     
%     if sum(rG1)>0
%         G1.rts=rts(rG1);
%         G1.rt=mean(G1.rts);
%         G1.rtv=var(G1.rts);
%         G1.err=err(rG1);
%         G1.errate=sum(G1.err)*100/numel(G1.rts);
%         stats.G1=G1;
%     end
%     if sum(rG2)>0
%         G2.rts=rts(rG2);
%         G2.rt=mean(G2.rts);
%         G2.rtv=var(G2.rts);
%         G2.err=err(rG2);
%         G2.errate=sum(G2.err)*100/numel(G2.rts);
%         stats.G2=G2;
%     end
%     if sum(rL1)>0
%         L1.rts=rts(rL1);
%         L1.rt=mean(L1.rts);
%         L1.rtv=var(L1.rts);
%         L1.err=err(rL1);
%         L1.errate=sum(L1.err)*100/numel(L1.rts);
%         stats.L1=L1;
%     end
%     if sum(rL2)>0
%         L2.rts=rts(rL2);
%         L2.rt=mean(L2.rts);
%         L2.rtv=var(L2.rts);
%         L2.err=err(rL2);
%         L2.errate=sum(L2.err)*100/numel(L2.rts);
%         stats.L2=L2;
%     end

    stats.type=type;
    stats.trials=trials;
    stats.rts=rts;
    stats.rt=rt;
    stats.rtv=rtv;
    stats.err=err;
    stats.errate=errate;
    stats.errate_unforced=errate_unforced;
    stats.chgtrials=ruleChg;
    stats.refcards=refcards;
    stats.targets=targets;
end