function data=readWCSTlog( fname )
% READWCSTLOG takes a filename and parses the given log file.
    
    if exist(fname, 'file')
        fid = fopen(fname);
        data = textscan(fid, '%s%s%s', 'Delimiter', '\t');
    else
        myReport( [fname ' does not exist. Abort'] );
        return;
    end
    time = cellfun(@str2double, data{1} );
    trig = data{3};
    thr=find(~cellfun(@isempty, strfind(trig, 'Running set')));
    thr=thr(1)-1;
    time(1:thr)=[];
    head=trig{1:thr};
    trig(1:thr)=[];
end