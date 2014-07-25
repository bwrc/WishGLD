function data=readWCSTlog( filename )
% READWCSTLOG takes a filename or directory and parses the given log file(s)
    data=struct;
    [directory, fname, ext] = fileparts(filename);
    s = filesep;
    looper = 1;
    % If filename is a directory, not a file
    if isdir(filename)
        if ~isempty(ext) % if extension is not empty when filename is a directory, path contained period
            fname = strcat( fname, ext );
        end        
        % Make sure we have a well formed path with separators
        directory = fullfile(directory, fname, s);
        % Obtain all at once
        files = dir(strcat(directory, '*.log'));
        % Get complete path for files?
%         [directory,~,~]=fileparts(which(files(1).name));
        looper = numel(files);
    else
        % This is a single file case - check file exists, and check file format
        if exist( filename, 'file' ) && strcmpi( ext, '.log' )==1
            files=dir(filename);
        else
            disp('Bad file or filename - check and retry');
            return;
        end
    end
    for i=1:looper
        filename=files(i).name;
        temp=readonelog( filename );
        % cleanup and save
        save(temp.subj, '-struct', 'temp');
        data(i).(temp.subj)=temp;
    end
end

function data=readonelog( fname )
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
    
    %% extract the block headers indices and cut out 'escaped' blocks
    blockidx=find(~cellfun(@isempty, strfind(trig, 'Running set')));
    blockidx=[blockidx; numel(time)+1];
    badtrial=false(numel(time),1);
    for i=1:numel(blockidx)-1
        tmp_trig = trig(blockidx(i):blockidx(i+1)-1);
%         cue_l=~cellfun(@isempty, strfind(tmp_trig,'CUE'));
        tgt_l=~cellfun(@isempty, strfind(tmp_trig,'TGT'));
        rsp_l=~cellfun(@isempty, strfind(tmp_trig,'RESP'));
        % id trials where target has no response, and excise
        if sum(rsp_l) == 0
            badtrial(blockidx(i):blockidx(i+1)-1)=1;
        elseif sum(rsp_l) < sum(tgt_l)
            test=tgt_l-[rsp_l(2:end); 0];
            badtrial(blockidx(i):blockidx(i+1)-1)=...
                test | [test(2:end); 0] | [test(3:end); 0; 0];
        end
    end
    time(badtrial) = [];
    trig(badtrial) = [];
    
    %% get header info
    data=struct;
    data.subj = strrep(head{1}(10:end),'.','');
    data.date = datevec(head{2}(6:end));
    data.age = str2double(head{3}(6:end));
    data.group = head{4}(8:end);
    % get full dataset stats
    data.alltrials = getstats(time, trig, 'All Trials');
    
    %% get rules-based stats
    rule_ttl={'G1', 'G2', 'L1', 'L2'};
    for i=1:4
        trials=getruletrials(trig,rule_ttl{i});
        if sum(trials)>0
            data.rules.(rule_ttl{i}) =...
                getstats(time(trials), trig(trials), rule_ttl{i});
        end
    end

    %% get stats for presented blocks
    blockidx=find(~cellfun(@isempty, strfind(trig, 'Running set')));
    blockidx=[blockidx; numel(time)+1];
    for i=1:numel(blockidx)-1
        type = trig{blockidx(i)}(13:end-5);
        tmp_time = time(blockidx(i):blockidx(i+1)-1);
        tmp_trig = trig(blockidx(i):blockidx(i+1)-1);
        data.blocks(i).stats = getstats(tmp_time, tmp_trig, type);
        % per block rule stats
        for r=1:4
            trials=getruletrials(tmp_trig,rule_ttl{r});
            if sum(trials)>0
                data.blocks(i).(rule_ttl{r}) = getstats(tmp_time(trials),...
                                tmp_trig(trials), [type '_' rule_ttl{r}]);
            end
        end
    end
    
    %% get blocks for each stimulus category
    cats={'face', 'letters_of', 'noise',...
        'shape', 'of_letter', 'patch'};
%     cats={'face2', 'face4', 'letterDJLU', 'letterCGOQ', 'noise',...
%         'shape', 'letterWERP', 'patch'};
    % combine and grab block stats for each category
    for i=1:numel(cats)
        bgns=find(~cellfun(@isempty, strfind(trig,cats{i})));
        [agg_time, agg_trig]=getaggblocks(bgns, time, trig);
        if ~isempty(agg_time)
            data.(cats{i})=getstats(agg_time, agg_trig, cats{i});
        end
    end
    combos=[1 1 1 2 2 2 3 3;...
            4 5 6 4 5 6 4 5];
    for i=1:8
        bgn1=find(~cellfun(@isempty, strfind(trig,cats{combos(1,i)})));
        bgn2=find(~cellfun(@isempty, strfind(trig,cats{combos(2,i)})));
        if (~isempty(bgn1) && ~isempty(bgn2)) && (length(bgn1)~=length(bgn2) || ~isequal(bgn1, bgn2))
            [agg_time, agg_trig]=getaggblocks(intersect(bgn1, bgn2), time, trig);
            if ~isempty(agg_time)
                name=[cats{combos(1,i)} '_' cats{combos(2,i)}];
                data.(name)=getstats(agg_time, agg_trig, name);
            end
        end
    end
end

function [agg_time, agg_trig]=getaggblocks(bgns, time, trig)
    blockidx=find(~cellfun(@isempty, strfind(trig, 'Running set')));
    blockidx=[blockidx; numel(time)];
    ends=bgns;
    agg_time=[];
    agg_trig={};
    for b=1:numel(bgns)
        ends(b)=blockidx(find(blockidx>bgns(b), 1, 'first'))-1;
        agg_time=[agg_time; time(bgns(b):ends(b))]; %#ok<*AGROW>
        agg_trig=[agg_trig; trig(bgns(b):ends(b))];
    end
end

function trials=getruletrials(trig, rule)
    ridx=~cellfun(@isempty, strfind(trig,rule));
    decx=[ridx(2:end); 0];
    incx=[0; ridx(1:end-1)];
    trials=ridx | incx | decx;
end

function stats=getstats(time, trig, type)
    stats=struct;

%     cue_l=~cellfun(@isempty, strfind(trig,'CUE'));
    stm_l=~cellfun(@isempty, strfind(trig,'STIM'));
    tgt_l=~cellfun(@isempty, strfind(trig,'TGT'));
    rsp_l=~cellfun(@isempty, strfind(trig,'RESP'));
%     fdb_l=~cellfun(@isempty, strfind(trig,'FEEDB'));
%     cues=time(cue_l);
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
    try
        rts=time(rsp_l) - time(tgt_l); % response time measures lag from target presenation to response
    catch ME,
        disp([ME.message ' Mismatch of targets and responses! In block: ' type]);
    end
    rt=mean(rts);
    rtv=var(rts);
    err=cellfun(@isempty, strfind(resps,'RESP   0'));
    errate=sum(~err)*100/trials;
    errate_unforced=sum(~err(~ruleChg))*100/(trials-sum(ruleChg));
    
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