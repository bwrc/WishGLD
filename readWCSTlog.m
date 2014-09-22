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
% READONELONG parses a single log file: extracts trials of interest
% and compiles various stats calling getstats(), to build 'data'.

    % Read file
    if exist(fname, 'file')
        fid = fopen(fname);
        data = textscan(fid, '%s%s%s', 'Delimiter', '\t');
    else
        error( [fname ' does not exist. Abort'] );
    end
    %% extract time and trigger columns as vectors
    time = cellfun(@str2double, data{1} );
    trig = data{3};
    % trim data sets
    thr=find(~cellfun(@isempty, strfind(trig, '------------')));
    time(1:thr(2))=[];
    head=trig(1:thr(1)-1); % extract naming info
    trig(1:thr(2))=[];

    %% get header info
    data=struct;
    data.subj = strrep(head{1}(10:end),'.','');
    data.date = datevec(head{2}(6:end));
    data.age = str2double(head{3}(6:end));
    data.group = head{4}(8:end);
    
    %% extract the set headers indices and clean up:
    %   - cut out 'escaped' sets
    %   - cut out trials with no response
    setidx=find(~cellfun(@isempty, strfind(trig, 'Running set')));
    setnames=trig{setidx}; %#ok<NASGU>
    setidx=[setidx; numel(time)+1];
    badtrial=false(numel(time),1);
    for i=1:numel(setidx)-1
        tmp_trig = trig(setidx(i):setidx(i+1)-1);
        tgt_l=~cellfun(@isempty, strfind(tmp_trig,'TGT'));
        rsp_l=~cellfun(@isempty, strfind(tmp_trig,'RSP'));
        % id trials where target has no response, and excise
        if sum(rsp_l) == 0
            badtrial(setidx(i):setidx(i+1)-1)=1;
        elseif sum(rsp_l) < sum(tgt_l)
            test=tgt_l-[rsp_l(2:end); 0];
            badtrial(setidx(i):setidx(i+1)-1)=...
                test | [test(2:end); 0] | [test(3:end); 0; 0];
        end
    end
    time(badtrial) = [];    trig(badtrial) = [];
    
    % finally, get stats for complete dataset
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

    %% get stats for presented sets
    setidx=find(~cellfun(@isempty, strfind(trig, 'Running set')));
    setidx=[setidx; numel(time)+1];
    for i=1:numel(setidx)-1
        type = trig{setidx(i)}(13:end-5);
        tmp_time = time(setidx(i):setidx(i+1)-1);
        tmp_trig = trig(setidx(i):setidx(i+1)-1);
        data.sets(i).stats = getstats(tmp_time, tmp_trig, type);
        % per set rule stats
        for r=1:4
            trials=getruletrials(tmp_trig,rule_ttl{r});
            if sum(trials)>0
                data.sets(i).(rule_ttl{r}) = getstats(tmp_time(trials),...
                                tmp_trig(trials), [type '_' rule_ttl{r}]);
            end
        end
    end
    
    %% get sets for each stimulus category
%     cats=setnames;
%     idx=[cell2mat(strfind(cats,'\')) cell2mat(strfind(cats,'_'))];
%     for i=1:numel(cats)
%         cats{i}=cats{i}(idx(end-1):idx(end));
%     end
    cats={'\face', '\letter', '\noise',...
        '_shape', '_letter', '_patch'};
    % aggregate trials and grab set stats for each category
    for i=1:numel(cats)
        bgns=find(~cellfun(@isempty, strfind(trig,cats{i})));
        [agg_time, agg_trig]=getaggsets(bgns, time, trig);
        if ~isempty(agg_time)
            name=strrep(cats{i},'_','l_');
            name=strrep(name,'\','g_');
            data.(name)=getstats(agg_time, agg_trig, cats{i});
        end
    end
    %% do combinations of each category, i.e. face_shape, face_letter, etc
    combos=[1 1 1 2 2 2 3 3;...
            4 5 6 4 5 6 4 5];
    for i=1:8
        bgn1=find(~cellfun(@isempty, strfind(trig,cats{combos(1,i)})));
        bgn2=find(~cellfun(@isempty, strfind(trig,cats{combos(2,i)})));
        if (~isempty(bgn1) && ~isempty(bgn2)) &&...
                (length(bgn1)~=length(bgn2) || ~isequal(bgn1, bgn2))
            [agg_time, agg_trig]=getaggsets(intersect(bgn1, bgn2), time, trig);
            if ~isempty(agg_time)
                name=[cats{combos(1,i)}(2:end) '_' cats{combos(2,i)}(2:end)];
                data.(name)=getstats(agg_time, agg_trig, name);
            end
        end
    end
end

function [agg_time, agg_trig]=getaggsets(bgns, time, trig)
    setidx=find(~cellfun(@isempty, strfind(trig, 'Running set')));
    setidx=[setidx; numel(time)];
    ends=bgns;
    agg_time=[];
    agg_trig={};
    for b=1:numel(bgns)
        ends(b)=setidx(find(setidx>bgns(b), 1, 'first'))-1;
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
% GETSTATS parses collections of WCST log trials, extracting response
% statistics like RTV, hit rate etc.

    stats=struct;
    % ---------------------------------------------------------------------
    % delete header rows --------------------------------------------------
    sethdr=~cellfun(@isempty, strfind(trig, 'Running set'));
    time(sethdr)=[];    trig(sethdr)=[];
    temp=sethdr | [0; sethdr(1:end-1)];
    sethdr=temp(~sethdr);
    % ---------------------------------------------------------------------
    % parse NasaTLX response rows and delete ------------------------------
    setrsp=~cellfun(@isempty, strfind(trig, 'Ponnistelu'));
    temprsp=trig(setrsp);
    time(setrsp)=[];    trig(setrsp)=[];    sethdr(setrsp)=[];
    ponnis = zeros(numel(temprsp),2);
    for i=1:numel(temprsp)
        ponnis(i,1)=str2double(temprsp{i}(1));
        ponnis(i,2)=str2double(temprsp{i}(end));
    end
    setrsp=~cellfun(@isempty, strfind(trig, 'Turhautuminen'));
    temprsp=trig(setrsp);
    time(setrsp)=[];    trig(setrsp)=[];    sethdr(setrsp)=[];
    turhau = zeros(numel(temprsp),2);
    for i=1:numel(temprsp)
        turhau(i,1)=str2double(temprsp{i}(1));
        turhau(i,2)=str2double(temprsp{i}(end));
    end
    % ---------------------------------------------------------------------
    % extract the numbering for blocks and trials -------------------------
    numall=numel(trig);
    if mod(numall,5) ~= 0
        disp([type ' ::trials are not well formed despite attempted cleaning: aborting']);
        return;
    else
        trials=numel(trig)/5;
    end
    enum=zeros(trials*5,1);
    idx=cell2mat(strfind(trig,'_'));
    for i=1:trials*5
        enum(i)=str2double(trig{i}(1:idx(i)-1));
    end
%     alltrlidx=round(abs(enum-fix(enum)).*100);
    uniqum=unique(enum);
    trlidx=round(abs(uniqum-fix(uniqum)).*100);
    blocks=numel(unique(round(uniqum)));
    sethdrtr=sethdr(mod(1:numall,ones(1,numall).*5)==1);
    % ---------------------------------------------------------------------
    % index each trial-part: cue, stimulus, target, response, feedback ----
%     cue_l=~cellfun(@isempty, strfind(trig,'CUE'));
    stm_l=~cellfun(@isempty, strfind(trig,'STM'));
    tgt_l=~cellfun(@isempty, strfind(trig,'TGT'));
    rsp_l=~cellfun(@isempty, strfind(trig,'RSP'));
    fdb_l=~cellfun(@isempty, strfind(trig,'FDB'));
%     cues=time(cue_l);
    stims=trig(stm_l);
    trgts=trig(tgt_l);
    resps=trig(rsp_l);
    feedb=trig(fdb_l);
    % ---------------------------------------------------------------------
    % extract the target and reference cards shown ------------------------
    targets=NaN(4,trials);
    idx=cell2mat(strfind(stims,','));
    for i=1:trials
        targets(:,i)=cell2mat(textscan(stims{i}(idx(i,1)-1:idx(i,3)+1),'%d','Delimiter',','));
    end
    refcards=NaN(4,trials,4);
    idx=cell2mat(strfind(trgts,','));
    for i=1:trials
        refparts=textscan(trgts{i}(idx(i,1)-1:idx(i,12)+1),'%s%s%s%s','Delimiter',';');
        for j=1:4
            refcards(:,i,j)=cell2mat(textscan(refparts{j}{1},'%d','Delimiter',','));
        end
    end
    % ---------------------------------------------------------------------
    % extract indices of each rule type and changes between rules ---------
    rG1=~cellfun(@isempty, strfind(stims,'G1'));
    rG2=~cellfun(@isempty, strfind(stims,'G2'));
    rL1=~cellfun(@isempty, strfind(stims,'L1'));
    rL2=~cellfun(@isempty, strfind(stims,'L2'));
    idx=[find(sethdrtr); trials+1];
    numidx=numel(idx);
    numrules=zeros(numidx-1,1);
    for i=1:numidx-1
        numrules(i)=...
            (sum(rG1(idx(i):idx(i+1)-1))>0) + (sum(rG2(idx(i):idx(i+1)-1))>0)...
            + (sum(rL1(idx(i):idx(i+1)-1))>0) + (sum(rL2(idx(i):idx(i+1)-1))>0);
    end
    
    % ---------------------------------------------------------------------
    % finally, let's find statistics of this data set ---------------------
    
    try     % response time measures lag from target presenation to response
        rts=time(rsp_l) - time(tgt_l); 
    catch ME,
        disp([ME.message ' Mismatch of targets and responses! In set: ' type]);
    end
    err = ...                   % all errors
        ~cellfun(@isempty, strfind(resps,'RSP 0'));
    search = trlidx~=1 &...     % errors between rule change & 1st hit
        ~cellfun(@isempty, strfind(feedb,'FAIL 0 of'));
    fails = ...                 % errors after 1st hit
        ~cellfun(@isempty, strfind(feedb,'FAIL')) &...
        cellfun(@isempty, strfind(feedb,'FAIL 0 of'));
    hits = trlidx~=1 &...       % hits excluding on rule change (accidents)
        ~cellfun(@isempty, strfind(feedb,'CORRECT'));
    confhits = trlidx~=1 &...   % hits after confirmation
        cellfun(@isempty, strfind(feedb,'CORRECT 1 of'));
    
    rt=mean(rts);               % mean response time of all trials
    rtv=var(rts);               % response time variability of all trials
    errate=sum(err)*100/trials; % error rate of all trials
    errate_unforced=...         % error rate of non-rule-change trials
        sum(fails)*100/(trials-sum(trlidx==1));
    errunfrt=mean(rts(fails));  % response time of unforced, non-search error trials
    errunfrtv=var(rts(fails));  % rt variability of unforced, non-search error trials
    srchavg=sum(search)/blocks; % average number of trials spent searching
    srchrt=mean(rts(search));   % response time of search error trials
    srchrtv=var(rts(search));   % rt variability of search error trials
    hitrt=mean(rts(hits));      % response time of hit trials
    hitrtv=var(rts(hits));      % rt variability of hit trials
    cfhitrt=mean(rts(confhits));% response time of hit trials after first
    cfhitrtv=var(rts(confhits));% rt variability of hit trials after first

    % ---------------------------------------------------------------------
%     stats.enum=uniqum;
    stats.type=type;
    stats.trials=trials;
    stats.blocks=blocks;
%     stats.rts=rts;
    stats.rt=rt;
    stats.rtv=rtv;
%     stats.err=err;
    stats.errate=errate;
    stats.errate_unforced=errate_unforced;
    stats.err_unf_rt=errunfrt;
    stats.err_unf_rtv=errunfrtv;
    stats.search_avg=srchavg;
    stats.search_rt=srchrt;
    stats.search_rtv=srchrtv;
    stats.hits_rt=hitrt;
    stats.hits_rtv=hitrtv;
    stats.conf_hits_rt=cfhitrt;
    stats.conf_hits_rtv=cfhitrtv;
%     stats.chgtrials=ruleChg;
    stats.refcards=refcards;
    stats.targets=targets;
    stats.NasaTLX.ponnistelu_set_val=ponnis;
    stats.NasaTLX.turhautuminen_set_val=turhau;
end